<!DOCTYPE html>
<html lang="en">
<body>
    <div class="container">
        <h1>SUVIDHA - Centralised Smart Civic Services KIOSK And Digital Helpdesk Platform</h1>
        <p>SUVIDHA is a digital helpdesk platform designed to provide single-window access to multiple government and civic services such as utility bill payments, grievance registration, and service tracking. Built for the SUVIDHA 2026 Hackathon (State of Assam Problem Statement), this solution operates on touch-optimized kiosk systems, making digital governance accessible in rural, semi-urban, and urban settings.</p>

  <h2>🌟 Key Features</h2>
        <ul>
            <li><strong>Single-Window Access:</strong> Integrates disjointed government services into one unified interface.</li>
            <li><strong>Touch-Optimized Kiosk UI:</strong> Features large touch targets, high-contrast colors, and one-step-per-screen navigation designed specifically for public usage environments.</li>
            <li><strong>Multilingual &amp; Voice Guidance:</strong> Supports 12 regional languages with synchronized audio-visual highlights to assist users with low digital literacy.</li>
            <li><strong>Secure Bill Payments:</strong> Integrated payment processing for Electricity, Water, and Gas bills.</li>
            <li><strong>Smart Complaint Registration:</strong> Utilizes a root-cause branching decision tree to ensure precise categorization of civic issues.</li>
            <li><strong>Robust Security:</strong> Implements JWT-based authentication, rate limiting, and PostgreSQL with parameterized queries via a centralized Node.js API Gateway.</li>
        </ul>

  <h2>🏗️ System Architecture</h2>
        <p>SUVIDHA follows a modular microservice-based architecture:</p>
        <ul>
            <li><strong>Presentation Layer:</strong> Custom UI optimized for 21-inch touchscreen kiosks.</li>
            <li><strong>API Gateway:</strong> Node.js + Express centralized request handler enforcing JWT verification and rate limiting.</li>
            <li><strong>Data Layer:</strong> PostgreSQL database handling ACID-compliant transactions for payments, users, and audit logs.</li>
            <li><strong>External Integrations:</strong> Payment gateway (Square API in current prototype), SMS APIs, and State Utility Adapters.</li>
        </ul>

  <h2>🚀 Getting Started</h2>

  <h3>Prerequisites</h3>
        <ul>
            <li>Node.js (v16 or higher)</li>
            <li>PostgreSQL installed and running</li>
            <li>Square Developer Account (for payment sandbox credentials)</li>
        </ul>

  <h3>1. Database Setup</h3>
        <p>Ensure PostgreSQL is running on your machine (default port <code>5432</code>). Create a new database for the project:</p>
        <pre><code>CREATE DATABASE suvidha_db;</code></pre>
        <p><em>(Note: The Node.js server will automatically initialize the required tables <code>users</code>, <code>bills</code>, <code>payments</code>, and <code>complaints</code> on its first run).</em></p>

  <h3>2. Backend Installation (API Gateway)</h3>
        <p>Navigate to the backend directory and install dependencies:</p>
        <pre><code>npm install express cors jsonwebtoken pg express-rate-limit square dotenv crypto</code></pre>

  <h3>3. Environment Variables</h3>
        <p>Create a <code>.env</code> file in the root directory and add the following configurations:</p>
        <pre><code>PORT=5000
JWT_SECRET=your_super_secret_jwt_key

# PostgreSQL Configuration
DB_USER=postgres
DB_HOST=localhost
DB_NAME=suvidha_db
DB_PASSWORD=your_db_password
DB_PORT=5432

# Square Payment Gateway
SQUARE_ACCESS_TOKEN=your_square_sandbox_access_token
SQUARE_ENVIRONMENT=sandbox
SQUARE_LOCATION_ID=your_square_location_id</code></pre>

  <h3>4. Running the Server</h3>
        <p>Start the backend API gateway:</p>
        <pre><code>node server.js</code></pre>
        <p>The server will start on <code>http://localhost:5000</code> and initialize the database tables.</p>

  <h3>5. Launching the Frontend Kiosk</h3>
        <p>The frontend is a lightweight, dependency-free vanilla HTML/JS application tailored for kiosk browsers.</p>
        <ol>
            <li>Open <code>index.html</code> in a modern web browser (Chrome/Edge recommended).</li>
            <li>For the intended kiosk experience, press <code>F11</code> to enter fullscreen mode.</li>
        </ol>

  <h2>🧪 Testing the Prototype</h2>
        <ul>
            <li><strong>Authentication:</strong> When prompted for an Aadhaar scan/entry, input any 12-digit number. The prototype OTP for verification is hardcoded to <code>123456</code>.</li>
            <li><strong>Payments:</strong> The sandbox environment uses simulated Square payments. Linking a new bill will fetch mock BBPS data.</li>
        </ul>

<h2>👥 Team</h2>
        <p>Developed by <strong>Team HACKONAUTS</strong>:</p>
        <ul>
            <li><strong>Parth Wade:</strong> Team Leader &amp; Project Manager</li>
            <li><strong>Divyank Singh:</strong> System Designer</li>
            <li><strong>Ritesh Verma:</strong> Backend Developer</li>
            <li><strong>Darshan Ambekar:</strong> UI/UX Designer</li>
        </ul>
    </div>
</body>
</html>
