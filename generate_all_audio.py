import os
import requests
import urllib.parse
import torch
import scipy.io.wavfile
from transformers import VitsModel, AutoTokenizer

output_dir = "kiosk_audio"
os.makedirs(output_dir, exist_ok=True)

# The Complete Production UI Dictionary Keys
audio_keys = [
    'your_bills', 'services', 'comp_cat',
    'srv_comp', 'srv_hist', 'srv_ai', 'srv_gov', 'srv_doc', 'srv_support',
    'pay_scan', 'pay_processing', 'pay_success', 'pay_fail',
    'add_bill_tenant', 'support_ticket_raised', 'support_printer_empty', 'print_receipt',
    'tree_water_q', 'tree_w_nowater', 'tree_w_dirty', 'tree_w_pressure',
    'tree_elec_q', 'tree_e_cut', 'tree_e_volt', 'tree_e_spark',
    'tree_ticket_success'
]

# Master Translations for all 12 Languages
translations = {
    'en': {
        'your_bills': 'Your Bills', 'services': 'Civic Services', 'comp_cat': 'Select Affected Service',
        'srv_comp': 'Register Complaint', 'srv_hist': 'History Vault', 'srv_ai': 'AI Helpdesk', 'srv_gov': 'Government Schemes', 'srv_doc': 'Print Documents', 'srv_support': 'Kiosk Support',
        'pay_scan': 'Please scan the QR code to pay', 'pay_processing': 'Processing payment, please wait', 'pay_success': 'Payment successful. Printing receipt.', 'pay_fail': 'Payment failed. Please try again.',
        'add_bill_tenant': 'Name mismatch. Adding as Tenant.', 'support_ticket_raised': 'Ticket raised. Issue will resolve in 2 hours.', 'support_printer_empty': 'Printer empty. Receipt sent via SMS.', 'print_receipt': 'Please collect your printed receipt.',
        'tree_water_q': 'What is the issue with your Water supply?', 'tree_w_nowater': 'No Water', 'tree_w_dirty': 'Contaminated Water', 'tree_w_pressure': 'Low Pressure',
        'tree_elec_q': 'What is the electricity issue?', 'tree_e_cut': 'Power Cut', 'tree_e_volt': 'Voltage Fluctuations', 'tree_e_spark': 'Sparking Pole',
        'tree_ticket_success': 'Ticket raised successfully. Technicians dispatched.'
    },
    'hi': {
        'your_bills': 'आपके बिल', 'services': 'नागरिक सेवाएं', 'comp_cat': 'प्रभावित सेवा चुनें',
        'srv_comp': 'शिकायत दर्ज करें', 'srv_hist': 'इतिहास वॉल्ट', 'srv_ai': 'AI सहायता', 'srv_gov': 'सरकारी योजनाएं', 'srv_doc': 'दस्तावेज़ प्रिंट करें', 'srv_support': 'कियोस्क सहायता',
        'pay_scan': 'कृपया भुगतान के लिए QR कोड स्कैन करें', 'pay_processing': 'भुगतान संसाधित हो रहा है, कृपया प्रतीक्षा करें', 'pay_success': 'भुगतान सफल। रसीद प्रिंट हो रही है।', 'pay_fail': 'भुगतान विफल। कृपया पुनः प्रयास करें।',
        'add_bill_tenant': 'नाम मेल नहीं खाता। किरायेदार के रूप में जोड़ रहे हैं।', 'support_ticket_raised': 'टिकट दर्ज किया गया। 2 घंटे में समाधान होगा।', 'support_printer_empty': 'प्रिंटर खाली है। रसीद SMS द्वारा भेजी गई।', 'print_receipt': 'कृपया अपनी रसीद लें।',
        'tree_water_q': 'आपकी जल आपूर्ति में क्या समस्या है?', 'tree_w_nowater': 'पानी नहीं आ रहा', 'tree_w_dirty': 'दूषित पानी', 'tree_w_pressure': 'कम दबाव',
        'tree_elec_q': 'बिजली की क्या समस्या है?', 'tree_e_cut': 'बिजली कटौती', 'tree_e_volt': 'वोल्टेज में उतार-चढ़ाव', 'tree_e_spark': 'खंभे में स्पार्किंग',
        'tree_ticket_success': 'टिकट सफलतापूर्वक दर्ज किया गया। तकनीशियन भेजे गए।'
    },
    'mr': {
        'your_bills': 'तुमची बिले', 'services': 'नागरी सेवा', 'comp_cat': 'प्रभावित सेवा निवडा',
        'srv_comp': 'तक्रार नोंदवा', 'srv_hist': 'इतिहास व्हॉल्ट', 'srv_ai': 'AI मदत', 'srv_gov': 'सरकारी योजना', 'srv_doc': 'कागदपत्रे प्रिंट करा', 'srv_support': 'कियोस्क मदत',
        'pay_scan': 'पैसे भरण्यासाठी कृपया QR कोड स्कॅन करा', 'pay_processing': 'पेमेंटवर प्रक्रिया होत आहे, कृपया प्रतीक्षा करा', 'pay_success': 'पेमेंट यशस्वी. पावती प्रिंट होत आहे.', 'pay_fail': 'पेमेंट अयशस्वी. कृपया पुन्हा प्रयत्न करा.',
        'add_bill_tenant': 'नाव जुळत नाही. भाडेकरू म्हणून जोडत आहे.', 'support_ticket_raised': 'तिकीट नोंदवले. २ तासात सुटेल.', 'support_printer_empty': 'प्रिंटर रिकामा आहे. पावती SMS द्वारे पाठवली.', 'print_receipt': 'कृपया तुमची पावती घ्या.',
        'tree_water_q': 'तुमच्या पाणीपुरवठ्यात काय समस्या आहे?', 'tree_w_nowater': 'पाणी नाही', 'tree_w_dirty': 'दूषित पाणी', 'tree_w_pressure': 'कमी दाब',
        'tree_elec_q': 'विजेची काय समस्या आहे?', 'tree_e_cut': 'वीज कपात', 'tree_e_volt': 'व्होल्टेजमध्ये चढउतार', 'tree_e_spark': 'खांबाला स्पार्किंग',
        'tree_ticket_success': 'तिकीट यशस्वीरित्या नोंदवले. तंत्रज्ञ पाठवले.'
    },
    'gu': {
        'your_bills': 'તમારા બિલ', 'services': 'નાગરિક સેવાઓ', 'comp_cat': 'પ્રભાવિત સેવા પસંદ કરો',
        'srv_comp': 'ફરિયાદ નોંધાવો', 'srv_hist': 'ઇતિહાસ વૉલ્ટ', 'srv_ai': 'AI હેલ્પડેસ્ક', 'srv_gov': 'સરકારી યોજનાઓ', 'srv_doc': 'દસ્તાવેજો પ્રિન્ટ કરો', 'srv_support': 'કિઓસ્ક સપોર્ટ',
        'pay_scan': 'ચૂકવણી કરવા માટે કૃપા કરીને QR કોડ સ્કેન કરો', 'pay_processing': 'ચુકવણીની પ્રક્રિયા થઈ રહી છે, કૃપા કરીને રાહ જુઓ', 'pay_success': 'ચુકવણી સફળ. રસીદ પ્રિન્ટ થઈ રહી છે.', 'pay_fail': 'ચુકવણી નિષ્ફળ. કૃપા કરીને ફરી પ્રયાસ કરો.',
        'add_bill_tenant': 'નામ મેળ ખાતું નથી. ભાડૂત તરીકે ઉમેરી રહ્યા છીએ.', 'support_ticket_raised': 'ટિકિટ નોંધાઈ ગઈ. 2 કલાકમાં ઉકેલ આવશે.', 'support_printer_empty': 'પ્રિન્ટર ખાલી છે. SMS દ્વારા રસીદ મોકલી.', 'print_receipt': 'કૃપા કરીને તમારી પ્રિન્ટેડ રસીદ લો.',
        'tree_water_q': 'તમારા પાણી પુરવઠામાં શું સમસ્યા છે?', 'tree_w_nowater': 'પાણી નથી', 'tree_w_dirty': 'દૂષિત પાણી', 'tree_w_pressure': 'ઓછું દબાણ',
        'tree_elec_q': 'વીજળીની શું સમસ્યા છે?', 'tree_e_cut': 'પાવર કટ', 'tree_e_volt': 'વોલ્ટેજ વધઘટ', 'tree_e_spark': 'થાંભલામાં સ્પાર્કિંગ',
        'tree_ticket_success': 'ટિકિટ સફળતાપૂર્વક નોંધાઈ. ટેકનિશિયન મોકલ્યા.'
    },
    'kn': {
        'your_bills': 'ನಿಮ್ಮ ಬಿಲ್‌ಗಳು', 'services': 'ನಾಗರಿಕ ಸೇವೆಗಳು', 'comp_cat': 'ಪೀಡಿತ ಸೇವೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ',
        'srv_comp': 'ದೂರು ನೋಂದಾಯಿಸಿ', 'srv_hist': 'ಇತಿಹಾಸ ವಾಲ್ಟ್', 'srv_ai': 'AI ಸಹಾಯವಾಣಿ', 'srv_gov': 'ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು', 'srv_doc': 'ದಾಖಲೆಗಳನ್ನು ಮುದ್ರಿಸಿ', 'srv_support': 'ಕಿಯೋಸ್ಕ್ ಬೆಂಬಲ',
        'pay_scan': 'ಪಾವತಿಸಲು ದಯವಿಟ್ಟು QR ಕೋಡ್ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ', 'pay_processing': 'ಪಾವತಿಯನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲಾಗುತ್ತಿದೆ, ದಯವಿಟ್ಟು ಕಾಯಿರಿ', 'pay_success': 'ಪಾವತಿ ಯಶಸ್ವಿಯಾಗಿದೆ. ರಶೀದಿ ಮುದ್ರಿಸಲಾಗುತ್ತಿದೆ.', 'pay_fail': 'ಪಾವತಿ ವಿಫಲವಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
        'add_bill_tenant': 'ಹೆಸರು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ. ಬಾಡಿಗೆದಾರರಾಗಿ ಸೇರಿಸಲಾಗುತ್ತಿದೆ.', 'support_ticket_raised': 'ಟಿಕೆಟ್ ರೈಸ್ ಮಾಡಲಾಗಿದೆ. 2 ಗಂಟೆಗಳಲ್ಲಿ ಪರಿಹರಿಸಲಾಗುವುದು.', 'support_printer_empty': 'ಪ್ರಿಂಟರ್ ಖಾಲಿ ಇದೆ. SMS ಮೂಲಕ ರಶೀದಿ ಕಳುಹಿಸಲಾಗಿದೆ.', 'print_receipt': 'ದಯವಿಟ್ಟು ನಿಮ್ಮ ಮುದ್ರಿತ ರಶೀದಿಯನ್ನು ಸಂಗ್ರಹಿಸಿ.',
        'tree_water_q': 'ನಿಮ್ಮ ನೀರು ಸರಬರಾಜಿನಲ್ಲಿ ಏನು ಸಮಸ್ಯೆ ಇದೆ?', 'tree_w_nowater': 'ನೀರಿಲ್ಲ', 'tree_w_dirty': 'ಕಲುಷಿತ ನೀರು', 'tree_w_pressure': 'ಕಡಿಮೆ ಒತ್ತಡ',
        'tree_elec_q': 'ವಿದ್ಯುತ್ ಸಮಸ್ಯೆ ಏನು?', 'tree_e_cut': 'ವಿದ್ಯುತ್ ಕಡಿತ', 'tree_e_volt': 'ವೋಲ್ಟೇಜ್ ಏರಿಳಿತಗಳು', 'tree_e_spark': 'ಕಂಬದಲ್ಲಿ ಸ್ಪಾರ್ಕಿಂಗ್',
        'tree_ticket_success': 'ಟಿಕೆಟ್ ಯಶಸ್ವಿಯಾಗಿ ರೈಸ್ ಮಾಡಲಾಗಿದೆ. ತಂತ್ರಜ್ಞರನ್ನು ಕಳುಹಿಸಲಾಗಿದೆ.'
    },
    'ta': {
        'your_bills': 'உங்கள் பில்கள்', 'services': 'குடிமக்கள் சேவைகள்', 'comp_cat': 'பாதிக்கப்பட்ட சேவையைத் தேர்ந்தெடுக்கவும்',
        'srv_comp': 'புகார் பதிவு செய்', 'srv_hist': 'வரலாறு பெட்டகம்', 'srv_ai': 'AI உதவி மையம்', 'srv_gov': 'அரசு திட்டங்கள்', 'srv_doc': 'ஆவணங்களை அச்சிடு', 'srv_support': 'கியோஸ்க் ஆதரவு',
        'pay_scan': 'பணம் செலுத்த QR குறியீட்டை ஸ்கேன் செய்யவும்', 'pay_processing': 'பணம் செயலாக்கப்படுகிறது, காத்திருக்கவும்', 'pay_success': 'பணம் செலுத்துதல் வெற்றி. ரசீது அச்சிடப்படுகிறது.', 'pay_fail': 'பணம் செலுத்துதல் தோல்வி. மீண்டும் முயற்சிக்கவும்.',
        'add_bill_tenant': 'பெயர் பொருந்தவில்லை. குத்தகைதாரராக சேர்க்கப்படுகிறது.', 'support_ticket_raised': 'டிக்கெட் பதிவு செய்யப்பட்டது. 2 மணி நேரத்தில் தீர்க்கப்படும்.', 'support_printer_empty': 'பிரிண்டர் காலியாக உள்ளது. SMS மூலம் ரசீது அனுப்பப்பட்டது.', 'print_receipt': 'தயவுசெய்து உங்கள் ரசீதை எடுத்துக்கொள்ளவும்.',
        'tree_water_q': 'உங்கள் நீர் விநியோகத்தில் என்ன பிரச்சனை?', 'tree_w_nowater': 'தண்ணீர் இல்லை', 'tree_w_dirty': 'மாசடைந்த தண்ணீர்', 'tree_w_pressure': 'குறைந்த அழுத்தம்',
        'tree_elec_q': 'மின்சார பிரச்சனை என்ன?', 'tree_e_cut': 'மின் தடை', 'tree_e_volt': 'மின்னழுத்த ஏற்ற இறக்கம்', 'tree_e_spark': 'கம்பத்தில் தீப்பொறி',
        'tree_ticket_success': 'டிக்கெட் வெற்றிகரமாக பதிவு செய்யப்பட்டது. தொழில்நுட்ப வல்லுநர்கள் அனுப்பப்பட்டனர்.'
    },
    'te': {
        'your_bills': 'మీ బిల్లులు', 'services': 'పౌర సేవలు', 'comp_cat': 'ప్రభావిత సేవను ఎంచుకోండి',
        'srv_comp': 'ఫిర్యాదు నమోదు చేయండి', 'srv_hist': 'చరిత్ర వాల్ట్', 'srv_ai': 'AI హెల్ప్‌డెస్క్', 'srv_gov': 'ప్రభుత్వ పథకాలు', 'srv_doc': 'పత్రాలను ముద్రించండి', 'srv_support': 'కియోస్క్ మద్దతు',
        'pay_scan': 'చెల్లించడానికి దయచేసి QR కోడ్‌ని స్కాన్ చేయండి', 'pay_processing': 'చెల్లింపు ప్రాసెస్ చేయబడుతోంది, దయచేసి వేచి ఉండండి', 'pay_success': 'చెల్లింపు విజయవంతమైంది. రసీదు ప్రింట్ చేయబడుతోంది.', 'pay_fail': 'చెల్లింపు విఫలమైంది. దయచేసి మళ్లీ ప్రయత్నించండి.',
        'add_bill_tenant': 'పేరు సరిపోలలేదు. అద్దెదారుగా జోడిస్తున్నాము.', 'support_ticket_raised': 'టికెట్ నమోదు చేయబడింది. 2 గంటల్లో పరిష్కరించబడుతుంది.', 'support_printer_empty': 'ప్రింటర్ ఖాళీగా ఉంది. SMS ద్వారా రసీదు పంపబడింది.', 'print_receipt': 'దయచేసి మీ రసీదుని తీసుకోండి.',
        'tree_water_q': 'మీ నీటి సరఫరాలో సమస్య ఏమిటి?', 'tree_w_nowater': 'నీరు లేదు', 'tree_w_dirty': 'కలుషిత నీరు', 'tree_w_pressure': 'తక్కువ పీడనం',
        'tree_elec_q': 'విద్యుత్ సమస్య ఏమిటి?', 'tree_e_cut': 'విద్యుత్ కోత', 'tree_e_volt': 'వోల్టేజ్ హెచ్చుతగ్గులు', 'tree_e_spark': 'స్తంభంలో స్పార్కింగ్',
        'tree_ticket_success': 'టికెట్ విజయవంతంగా నమోదు చేయబడింది. సాంకేతిక నిపుణులు పంపబడ్డారు.'
    },
    'bn': {
        'your_bills': 'আপনার বিল', 'services': 'নাগরিক পরিষেবা', 'comp_cat': 'প্রভাবিত পরিষেবা নির্বাচন করুন',
        'srv_comp': 'অভিযোগ দায়ের করুন', 'srv_hist': 'ইতিহাস ভল্ট', 'srv_ai': 'AI হেল্পডেস্ক', 'srv_gov': 'সরকারি প্রকল্প', 'srv_doc': 'নথি প্রিন্ট করুন', 'srv_support': 'কিয়স্ক সহায়তা',
        'pay_scan': 'পেমেন্ট করতে অনুগ্রহ করে QR কোড স্ক্যান করুন', 'pay_processing': 'পেমেন্ট প্রক্রিয়া করা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন', 'pay_success': 'পেমেন্ট সফল। রসিদ প্রিন্ট করা হচ্ছে।', 'pay_fail': 'পেমেন্ট ব্যর্থ হয়েছে। আবার চেষ্টা করুন।',
        'add_bill_tenant': 'নাম মিলছে না। ভাড়াটে হিসাবে যোগ করা হচ্ছে।', 'support_ticket_raised': 'টিকিট জমা দেওয়া হয়েছে। 2 ঘণ্টার মধ্যে সমাধান হবে।', 'support_printer_empty': 'প্রিন্টার খালি। SMS এর মাধ্যমে রসিদ পাঠানো হয়েছে।', 'print_receipt': 'অনুগ্রহ করে আপনার রসিদ সংগ্রহ করুন।',
        'tree_water_q': 'আপনার জল সরবরাহে কী সমস্যা?', 'tree_w_nowater': 'জল নেই', 'tree_w_dirty': 'দূষিত জল', 'tree_w_pressure': 'কম চাপ',
        'tree_elec_q': 'বিদ্যুতের সমস্যা কী?', 'tree_e_cut': 'বিদ্যুৎ বিভ্রাট', 'tree_e_volt': 'ভোল্টেজের ওঠানামা', 'tree_e_spark': 'খুঁটিতে স্পার্কিং',
        'tree_ticket_success': 'টিকিট সফলভাবে জমা দেওয়া হয়েছে। টেকনিশিয়ান পাঠানো হয়েছে।'
    },
    'pa': {
        'your_bills': 'ਤੁਹਾਡੇ ਬਿੱਲ', 'services': 'ਨਾਗਰਿਕ ਸੇਵਾਵਾਂ', 'comp_cat': 'ਪ੍ਰਭਾਵਿਤ ਸੇਵਾ ਚੁਣੋ',
        'srv_comp': 'ਸ਼ਿਕਾਇਤ ਦਰਜ ਕਰੋ', 'srv_hist': 'ਇਤਿਹਾਸ ਵਾਲਟ', 'srv_ai': 'AI ਹੈਲਪਡੈਸਕ', 'srv_gov': 'ਸਰਕਾਰੀ ਸਕੀਮਾਂ', 'srv_doc': 'ਦਸਤਾਵੇਜ਼ ਪ੍ਰਿੰਟ ਕਰੋ', 'srv_support': 'ਕਿਓਸਕ ਸਹਾਇਤਾ',
        'pay_scan': 'ਭੁਗਤਾਨ ਕਰਨ ਲਈ ਕਿਰਪਾ ਕਰਕੇ QR ਕੋਡ ਸਕੈਨ ਕਰੋ', 'pay_processing': 'ਭੁਗਤਾਨ ਦੀ ਪ੍ਰਕਿਰਿਆ ਹੋ ਰਹੀ ਹੈ, ਕਿਰਪਾ ਕਰਕੇ ਉਡੀਕ ਕਰੋ', 'pay_success': 'ਭੁਗਤਾਨ ਸਫਲ ਰਿਹਾ। ਰਸੀਦ ਪ੍ਰਿੰਟ ਹੋ ਰਹੀ ਹੈ।', 'pay_fail': 'ਭੁਗਤਾਨ ਅਸਫਲ ਰਿਹਾ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।',
        'add_bill_tenant': 'ਨਾਮ ਮੇਲ ਨਹੀਂ ਖਾਂਦਾ। ਕਿਰਾਏਦਾਰ ਵਜੋਂ ਸ਼ਾਮਲ ਕਰ ਰਹੇ ਹਾਂ।', 'support_ticket_raised': 'ਟਿਕਟ ਦਰਜ ਕੀਤੀ ਗਈ। 2 ਘੰਟਿਆਂ ਵਿੱਚ ਹੱਲ ਹੋ ਜਾਵੇਗਾ।', 'support_printer_empty': 'ਪ੍ਰਿੰਟਰ ਖਾਲੀ ਹੈ। ਰਸੀਦ SMS ਰਾਹੀਂ ਭੇਜੀ ਗਈ।', 'print_receipt': 'ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੀ ਰਸੀਦ ਲਓ।',
        'tree_water_q': 'ਤੁਹਾਡੀ ਪਾਣੀ ਦੀ ਸਪਲਾਈ ਵਿੱਚ ਕੀ ਸਮੱਸਿਆ ਹੈ?', 'tree_w_nowater': 'ਪਾਣੀ ਨਹੀਂ', 'tree_w_dirty': 'ਦੂਸ਼ਿਤ ਪਾਣੀ', 'tree_w_pressure': 'ਘੱਟ ਦਬਾਅ',
        'tree_elec_q': 'ਬਿਜਲੀ ਦੀ ਸਮੱਸਿਆ ਕੀ ਹੈ?', 'tree_e_cut': 'ਬਿਜਲੀ ਕੱਟ', 'tree_e_volt': 'ਵੋਲਟੇਜ ਵਿੱਚ ਉਤਰਾਅ-ਚੜ੍ਹਾਅ', 'tree_e_spark': 'ਖੰਭੇ ਵਿੱਚ ਸਪਾਰਕਿੰਗ',
        'tree_ticket_success': 'ਟਿਕਟ ਸਫਲਤਾਪੂਰਵਕ ਦਰਜ ਕੀਤੀ ਗਈ। ਟੈਕਨੀਸ਼ੀਅਨ ਭੇਜੇ ਗਏ।'
    },
    'ml': {
        'your_bills': 'നിങ്ങളുടെ ബില്ലുകൾ', 'services': 'പൗര സേവനങ്ങൾ', 'comp_cat': 'ബാധിച്ച സേവനം തിരഞ്ഞെടുക്കുക',
        'srv_comp': 'പരാതി രജിസ്റ്റർ ചെയ്യുക', 'srv_hist': 'ചരിത്ര വോൾട്ട്', 'srv_ai': 'AI ഹെൽപ്പ്ഡെസ്ക്', 'srv_gov': 'സർക്കാർ പദ്ധതികൾ', 'srv_doc': 'രേഖകൾ പ്രിന്റ് ചെയ്യുക', 'srv_support': 'കിയോസ്ക് പിന്തുണ',
        'pay_scan': 'പണമടയ്ക്കാൻ QR കോഡ് സ്കാൻ ചെയ്യുക', 'pay_processing': 'പണമടയ്ക്കൽ പ്രോസസ്സ് ചെയ്യുന്നു, കാത്തിരിക്കുക', 'pay_success': 'പണമടയ്ക്കൽ വിജയിച്ചു. രസീത് പ്രിന്റ് ചെയ്യുന്നു.', 'pay_fail': 'പണമടയ്ക്കൽ പരാജയപ്പെട്ടു. വീണ്ടും ശ്രമിക്കുക.',
        'add_bill_tenant': 'പേര് യോജിക്കുന്നില്ല. വാടകക്കാരനായി ചേർക്കുന്നു.', 'support_ticket_raised': 'ടിക്കറ്റ് രജിസ്റ്റർ ചെയ്തു. 2 മണിക്കൂറിനുള്ളിൽ പരിഹരിക്കും.', 'support_printer_empty': 'പ്രിന്റർ കാലിയാണ്. രസീത് SMS വഴി അയച്ചു.', 'print_receipt': 'ദയവായി നിങ്ങളുടെ രസീത് എടുക്കുക.',
        'tree_water_q': 'നിങ്ങളുടെ ജലവിതരണത്തിലെ പ്രശ്നം എന്താണ്?', 'tree_w_nowater': 'വെള്ളമില്ല', 'tree_w_dirty': 'മലിനജലം', 'tree_w_pressure': 'കുറഞ്ഞ മർദ്ദം',
        'tree_elec_q': 'വൈദ്യുതി പ്രശ്നം എന്താണ്?', 'tree_e_cut': 'വൈദ്യുതി തടസ്സം', 'tree_e_volt': 'വോൾട്ടേജ് വ്യതിയാനം', 'tree_e_spark': 'പോസ്റ്റിൽ തീപ്പൊരി',
        'tree_ticket_success': 'ടിക്കറ്റ് വിജയകരമായി രജിസ്റ്റർ ചെയ്തു. സാങ്കേതിക വിദഗ്ധരെ അയച്ചു.'
    },
    'or': {
        'your_bills': 'ଆପଣଙ୍କର ବିଲ୍', 'services': 'ନାଗରିକ ସେବା', 'comp_cat': 'ପ୍ରଭାବିତ ସେବା ବାଛନ୍ତୁ',
        'srv_comp': 'ଅଭିଯୋଗ ପଞ୍ଜିକରଣ କରନ୍ତୁ', 'srv_hist': 'ଇତିହାସ ଭଲ୍ଟ', 'srv_ai': 'AI ହେଲ୍ପଡେସ୍କ', 'srv_gov': 'ସରକାରୀ ଯୋଜନା', 'srv_doc': 'ଡକ୍ୟୁମେଣ୍ଟ୍ ପ୍ରିଣ୍ଟ କରନ୍ତୁ', 'srv_support': 'କିଓସ୍କ ସମର୍ଥନ',
        'pay_scan': 'ପୈଠ କରିବାକୁ ଦୟାକରି QR କୋଡ୍ ସ୍କାନ୍ କରନ୍ତୁ', 'pay_processing': 'ପେମେଣ୍ଟ ପ୍ରକ୍ରିୟାକରଣ ଚାଲିଛି, ଦୟାକରି ଅପେକ୍ଷା କରନ୍ତୁ', 'pay_success': 'ପେମେଣ୍ଟ ସଫଳ ହୋଇଛି। ରସିଦ ପ୍ରିଣ୍ଟ ହେଉଛି।', 'pay_fail': 'ପେମେଣ୍ଟ ବିଫଳ ହୋଇଛି। ଦୟାକରି ପୁଣି ଚେଷ୍ଟା କରନ୍ତୁ।',
        'add_bill_tenant': 'ନାମ ମେଳ ଖାଉନାହିଁ। ଭଡାଟିଆ ଭାବରେ ଯୋଡୁଛି।', 'support_ticket_raised': 'ଟିକେଟ୍ ଦାଖଲ ହୋଇଛି। 2 ଘଣ୍ଟା ମଧ୍ୟରେ ସମାଧାନ ହେବ।', 'support_printer_empty': 'ପ୍ରିଣ୍ଟର୍ ଖାଲି ଅଛି। SMS ମାଧ୍ୟମରେ ରସିଦ ପଠାଗଲା।', 'print_receipt': 'ଦୟାକରି ଆପଣଙ୍କର ରସିଦ ସଂଗ୍ରହ କରନ୍ତୁ।',
        'tree_water_q': 'ଆପଣଙ୍କ ଜଳ ଯୋଗାଣରେ ସମସ୍ୟା କ’ଣ?', 'tree_w_nowater': 'ପାଣି ନାହିଁ', 'tree_w_dirty': 'ଦୂଷିତ ପାଣି', 'tree_w_pressure': 'କମ୍ ଚାପ',
        'tree_elec_q': 'ବିଦ୍ୟୁତ୍ ସମସ୍ୟା କ’ଣ?', 'tree_e_cut': 'ବିଦ୍ୟୁତ୍ କାଟ', 'tree_e_volt': 'ଭୋଲଟେଜ୍ ଉଠାପକା', 'tree_e_spark': 'ଖୁଣ୍ଟରେ ସ୍ପାର୍କିଂ',
        'tree_ticket_success': 'ଟିକେଟ୍ ସଫଳତାର ସହ ଦାଖଲ ହୋଇଛି। ଟେକ୍ନିସିଆନ୍ ପଠାଯାଇଛି।'
    },
    'as': {
        'your_bills': 'আপোনাৰ বিল', 'services': 'নাগৰিক সেৱা', 'comp_cat': 'প্ৰভাৱিত সেৱা বাছক',
        'srv_comp': 'অভিযোগ পঞ্জীয়ন কৰক', 'srv_hist': 'ইতিহাস ভল্ট', 'srv_ai': 'AI হেল্পডেস্ক', 'srv_gov': 'চৰকাৰী আঁচনি', 'srv_doc': 'নথিপত্ৰ প্ৰিণ্ট কৰক', 'srv_support': 'কিয়স্ক সমৰ্থন',
        'pay_scan': 'পৰিশোধ কৰিবলৈ অনুগ্ৰহ কৰি QR ক’ড স্কেন কৰক', 'pay_processing': 'পৰিশোধ প্ৰক্ৰিয়াকৰণ চলি আছে, অনুগ্ৰহ কৰি অপেক্ষা কৰক', 'pay_success': 'পৰিশোধ সফল। ৰচিদ প্ৰিণ্ট হৈ আছে।', 'pay_fail': 'পৰিশোধ ব্যৰ্থ হৈছে। অনুগ্ৰহ কৰি পুনৰ চেষ্টা কৰক।',
        'add_bill_tenant': 'নামৰ মিল নাই। ভাড়াতীয়া হিচাপে যোগ কৰা হৈছে।', 'support_ticket_raised': 'টিকট দাখিল কৰা হৈছে। ২ ঘণ্টাৰ ভিতৰত সমাধান হ’ব।', 'support_printer_empty': 'প্ৰিণ্টাৰ খালী। SMS-ৰ জৰিয়তে ৰচিদ পঠিওৱা হৈছে।', 'print_receipt': 'অনুগ্ৰহ কৰি আপোনাৰ ৰচিদ সংগ্ৰহ কৰক।',
        'tree_water_q': 'আপোনাৰ পানী যোগানৰ সমস্যা কি?', 'tree_w_nowater': 'পানী নাই', 'tree_w_dirty': 'দূষিত পানী', 'tree_w_pressure': 'কম চাপ',
        'tree_elec_q': 'বিদ্যুতৰ সমস্যা কি?', 'tree_e_cut': 'বিদ্যুৎ কৰ্তন', 'tree_e_volt': 'ভল্টেজৰ উঠা-নমা', 'tree_e_spark': 'খুঁটাত স্পাৰ্কিং',
        'tree_ticket_success': 'টিকট সফলতাৰে দাখিল কৰা হৈছে। টেকনিচিয়ান পঠিওৱা হৈছে।'
    }
}

print(f"--- Starting Master Audio Generation ({len(audio_keys)} keys x 12 languages) ---")

# 1. Google Translate API for the 10 standard languages
google_langs = ['en', 'hi', 'mr', 'gu', 'kn', 'ta', 'te', 'bn', 'pa', 'ml']

for lang_code in google_langs:
    print(f"\nProcessing Google TTS for: {lang_code.upper()}")
    for key in audio_keys:
        if key in translations[lang_code]:
            text = translations[lang_code][key]
            filepath = os.path.join(output_dir, f"{lang_code}_{key}.mp3")
            
            if not os.path.exists(filepath):
                url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={lang_code}&client=tw-ob&q={urllib.parse.quote(text)}"
                try:
                    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                    if response.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        print(f"  ✅ Saved: {key}")
                    else:
                        print(f"  ❌ Failed {key} (HTTP {response.status_code})")
                except Exception as e:
                    print(f"  ❌ Error on {key}: {e}")
            else:
                print(f"  ⏭️ Skipped: {key}")

# 2. Local AI Models for Assamese and Odia
print("\n--- Starting Local AI Generation (Assamese/Odia) ---")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using compute device: {device.upper()}")

local_langs = {
    'as': 'facebook/mms-tts-asm',
    'or': 'facebook/mms-tts-ory'
}

for lang_code, model_id in local_langs.items():
    print(f"\nLoading Local AI Model for {lang_code.upper()} ({model_id})...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = VitsModel.from_pretrained(model_id).to(device)
        
        for key in audio_keys:
            if key in translations[lang_code]:
                text = translations[lang_code][key]
                filepath = os.path.join(output_dir, f"{lang_code}_{key}.wav")
                
                if not os.path.exists(filepath):
                    print(f"  Generating: {key}...")
                    inputs = tokenizer(text, return_tensors="pt").to(device)
                    with torch.no_grad():
                        output = model(**inputs).waveform
                        
                    scipy.io.wavfile.write(filepath, model.config.sampling_rate, output.cpu().numpy().squeeze())
                    print(f"  ✅ Saved Local TTS: {filepath}")
                else:
                    print(f"  ⏭️ Skipped: {key}")
    except Exception as e:
        print(f"❌ Failed to load or run model for {lang_code}: {e}")

print("\n🎉 Master audio generation complete! All 324 files checked.")