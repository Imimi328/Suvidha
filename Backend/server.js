require('dotenv').config();
const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');
const rateLimit = require('express-rate-limit');
const { SquareClient, SquareEnvironment } = require('square'); 
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 5000;

// ==========================================
// 1. CLOUDFLARE / PROXY SETTINGS
// ==========================================
app.set('trust proxy', 1); 

app.use(cors());
app.use(express.json());

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, 
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
});
app.use('/api/', limiter);

// ==========================================
// 2. CLIENT CONFIGURATIONS
// ==========================================
const squareClient = new SquareClient({
    token: process.env.SQUARE_ACCESS_TOKEN,
    environment: process.env.SQUARE_ENVIRONMENT === 'production' 
                 ? SquareEnvironment.Production 
                 : SquareEnvironment.Sandbox,
});

const pool = new Pool({
    user: process.env.DB_USER || 'postgres',
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'suvidha_db',
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT || 5432,
});

// ==========================================
// 3. DATABASE INITIALIZATION
// ==========================================
const initDB = async () => {
    const createTablesQuery = `
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            phone VARCHAR(15) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS bills (
            id VARCHAR(50) PRIMARY KEY,
            consumer_id VARCHAR(50) NOT NULL,
            provider VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending'
        );
        CREATE TABLE IF NOT EXISTS payments (
            txn_id VARCHAR(100) PRIMARY KEY,
            bill_id VARCHAR(50),
            amount DECIMAL(10, 2) NOT NULL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'success'
        );
        CREATE TABLE IF NOT EXISTS complaints (
            ticket_id VARCHAR(50) PRIMARY KEY,
            category VARCHAR(50),
            department VARCHAR(100),
            details TEXT,
            status VARCHAR(20) DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    `;
    try {
        await pool.query(createTablesQuery);
        console.log("✅ Database tables initialized successfully.");
    } catch (err) {
        console.error("❌ Database initialization failed:", err.message);
    }
};
initDB();

// ==========================================
// 4. AUTH & ROUTES
// ==========================================
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) return res.status(401).json({ error: "Unauthorized" });

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: "Forbidden" });
        req.user = user;
        next();
    });
};

app.post('/api/auth/verify-otp', async (req, res) => {
    const { phone, otp } = req.body;
    if (otp === "123456") {
        try {
            await pool.query('INSERT INTO users (phone) VALUES ($1) ON CONFLICT (phone) DO NOTHING', [phone]);
            const accessToken = jwt.sign({ phone }, process.env.JWT_SECRET, { expiresIn: '1h' });
            res.json({ accessToken });
        } catch (err) { res.status(500).json({ error: "DB Error" }); }
    } else { res.status(401).json({ error: "Invalid OTP" }); }
});

app.get('/api/bills/:consumerId', authenticateToken, async (req, res) => {
    res.json({ id: `b1`, consumer: req.params.consumerId, amount: 12.40, provider: "MSEDCL", type: "electricity" });
});

app.post('/api/payments/create-order', authenticateToken, async (req, res) => {
    const { amount, receiptId, sourceId = 'cnon:card-nonce-ok' } = req.body;
    console.log(`🚀 Processing Payment Attempt: $${amount} for Bill ${receiptId}`);

    try {
        const amountValue = typeof amount === 'string' ? parseFloat(amount) : amount;
        const amountInCents = BigInt(Math.round(amountValue * 100));

        const { result } = await squareClient.payments.create({
            idempotencyKey: crypto.randomUUID(),
            sourceId: sourceId,
            amountMoney: {
                amount: amountInCents,
                currency: 'USD' 
            },
            locationId: process.env.SQUARE_LOCATION_ID
        });

        // Safe access to payment ID
        const txnId = result && result.payment ? result.payment.id : null;
        
        if (!txnId) {
            throw new Error("Square API returned success but no payment ID was found.");
        }

        await pool.query('INSERT INTO payments (txn_id, bill_id, amount) VALUES ($1, $2, $3)', [txnId, receiptId, amountValue]);
        
        console.log(`✅ Payment Success! TXN: ${txnId}`);
        res.json({ success: true, txnId: txnId });

    } catch (error) {
        console.error("❌ SQUARE API ERROR CAUGHT:");
        
        // This will now print the actual error reason from Square without crashing
        if (error.result && error.result.errors) {
            console.error(JSON.stringify(error.result.errors, null, 2));
        } else {
            console.error(error.message || error);
        }
        
        res.status(500).json({ 
            success: false, 
            error: "Payment Failed",
            details: error.message 
        });
    }
});

app.post('/api/complaints', authenticateToken, async (req, res) => {
    const complaintId = "SVD-" + Math.floor(Math.random() * 9999);
    try {
        await pool.query('INSERT INTO complaints (ticket_id, category, department, details) VALUES ($1, $2, $3, $4)', 
            [complaintId, req.body.category, req.body.department, req.body.details]);
        res.json({ complaintId });
    } catch (err) { res.status(500).json({ error: err.message }); }
});

app.listen(PORT, () => {
    console.log(`🚀 SUVIDHA API Gateway: http://localhost:${PORT}`);
    console.log(`🔗 Cloudflare Tunnel Target: http://127.0.0.1:${PORT}`);
});