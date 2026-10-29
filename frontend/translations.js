// =============================================================================
// CropCure AI - Multilingual Translation Dictionary & Utilities
// Supported Languages: English (en), Telugu (te), Hindi (hi)
// =============================================================================

const TRANSLATIONS = {
    en: {
        nav: {
            brand: "CropCure AI",
            home: "Home",
            diagnosis: "Diagnosis",
            schemes: "Government Schemes",
            shops: "Nearby Shops",
            experts: "Agriculture Experts",
            performance: "Model Performance",
            chat: "AI Assistant",
            about: "About"
        },
        common: {
            tagline: "AI-POWERED CROP HEALTH",
            copyright: "© 2026 CropCure AI. Academic Project.",
            clear: "Clear",
            loading: "Loading...",
            search: "Search",
            all: "All",
            retry: "Retry Loading",
            optional: "Optional",
            disclaimer: "Disclaimer",
            official_portal: "Visit Official Portal ↗",
            open_in_maps: "Open in Google Maps ↗",
            open_in_osm: "Open in OpenStreetMap ↗",
            get_directions: "Get Driving Directions ↗",
            verified: "Verified",
            verified_badge: "✓ Verified Central Scheme",
            footer_desc: "AI-powered crop disease diagnosis and agricultural assistance for Indian farmers."
        },
        hero: {
            title_prefix: "Smart Crop Disease",
            title_highlight: "Diagnosis",
            description: "Upload a crop leaf image and let CropCure AI analyze it using deep learning and provide treatment and prevention guidance.",
            start_button: "Start Diagnosis"
        },
        diagnosis: {
            section_label: "DISEASE DETECTION",
            title: "Analyze Your Crop",
            description: "Upload a clear image of a crop leaf to identify possible diseases.",
            upload_title: "Upload Leaf Image",
            upload_desc: "Choose a clear image of the affected plant leaf. Formats: JPG, PNG, WEBP.",
            choose_image: "Choose Leaf Image",
            analyze_button: "Analyze Disease",
            analyzing_button: "Analyzing Image...",
            result_label: "DIAGNOSIS REPORT",
            primary_title: "Primary Visual Diagnosis",
            uncertain_title: "Visual Diagnosis (Uncertain)",
            uncertain_badge: "Uncertain Diagnosis (< 50%)",
            low_conf_badge: "Low Confidence",
            high_conf_badge: "High Confidence",
            confidence_label: "Confidence Level",
            uncertain_warning_title: "⚠️ Uncertain Visual Diagnosis (< 50% Confidence)",
            uncertain_warning_desc: "Visual diagnosis is uncertain. The model identified multiple candidate possibilities. Review candidate symptoms before taking action.",
            top3_title: "Top-3 Candidate Predictions",
            top3_subtitle: "Compare symptoms among these candidates before taking treatment measures:",
            no_knowledge: "Agricultural knowledge not available for this disease in current database.",
            view_details: "Compare Symptoms & Advice"
        },
        cards: {
            symptoms_title: "Symptoms",
            treatment_title: "Recommended Treatment",
            prevention_title: "Prevention Advice",
            guidance_title: "AI Agricultural Guidance",
            ask_title: "Ask a Question About This Diagnosis",
            ask_placeholder: "Ask about organic remedies, spray timing, or symptoms...",
            ask_button: "Ask AI"
        },
        chat: {
            section_label: "RAG & LLM ASSISTANCE",
            title: "AI Agricultural Assistant",
            description: "Ask questions about crop diseases, organic care, government schemes, or farm management.",
            welcome_msg: "Hello! I am your CropCure AI agricultural assistant. You can ask me about crop diseases, symptoms, treatment, organic practices, and government farming schemes in English, Telugu, or Hindi.",
            placeholder: "Type your agricultural question here (in English, Telugu or Hindi)...",
            send_button: "Send",
            empty_error: "Please enter a question before sending."
        },
        schemes: {
            section_label: "GOVERNMENT OF INDIA INITIATIVES",
            title: "Government Agricultural Schemes & Subsidies",
            description: "Discover verified central agricultural schemes, financial assistance, crop insurance, micro-irrigation subsidies, and farming support programs for Indian farmers.",
            banner_title: "Verified Official Portals Directory",
            banner_badge: "Curated & Verified · October 2026",
            banner_text: "This directory compiles authentic central government agricultural initiatives for educational and agricultural assistance. All scheme details, eligibility guidelines, benefits, and application pathways are curated directly from authorized Government of India portals.",
            helpline_title: "Toll-Free Helplines:",
            search_placeholder: "Search schemes by name, keyword (e.g., insurance, subsidy, loan, seeds, drip)...",
            showing_text: "Showing",
            verified_count_text: "verified government schemes",
            benefits_heading: "Key Benefits & Assistance",
            eligibility_heading: "Eligibility Summary",
            steps_heading: "How to Apply (Verified Steps)",
            empty_title: "No Schemes Found",
            empty_desc: "No agricultural schemes matched your current search keyword or category filter.",
            reset_filters: "Reset All Filters"
        },
        shops: {
            section_label: "LOCAL AGRICULTURAL SUPPLIES",
            title: "Nearby Agricultural Input Shops",
            description: "Locate certified seed stores, fertilizer retailers, crop protection dealers, and agricultural equipment suppliers in your area.",
            banner_title: "External Maps Service & Agricultural Safety Notice",
            banner_text: "CropCure AI generates verified search queries that open directly in established external mapping services (Google Maps and OpenStreetMap). Real-time shop locations, phone numbers, customer reviews, and driving directions are hosted directly on the external map service.",
            location_label: "1. Enter Your Location (City, Town, Village, or PIN Code):",
            location_placeholder: "e.g., Pune, 411001, Karnal, Nashik, Patna...",
            detect_btn: "🎯 Use My Location (Optional)",
            find_btn: "🔍 Find Nearby Shops",
            category_label: "2. Select Supply Category:",
            results_for: "Agricultural Supply Options for:",
            supply_grid_heading: "Supply Categories in Your Area",
            tips_title: "Farmer Advisory: What to Check Before Purchasing Farm Inputs",
            prompt_title: "Find Verified Agricultural Input Dealers",
            prompt_desc: "Type your city, town, village name, or postal PIN code above and click 'Find Nearby Shops' to launch verified map directions for certified seeds, fertilizers, approved crop protection products, and farm equipment."
        },
        experts: {
            section_label: "INSTITUTIONAL EXTENSION & SCIENTIFIC ADVISORY",
            title: "Agriculture Expert Support & Extension Services",
            description: "Connect with certified agricultural scientists, Krishi Vigyan Kendras (KVKs), and government agricultural extension officers across India.",
            banner_title: "Official Agricultural Advisory & Preliminary Prediction Notice",
            banner_text: "CropCure AI provides computer-vision based preliminary assessments. Machine-learning predictions should never replace in-person physical crop inspection by certified agricultural scientists, especially before applying restricted or chemical treatments.",
            kcc_title: "National Kisan Call Centre (Toll-Free Hotline)",
            kcc_number: "1800-180-1551",
            kcc_desc: "Direct telephone access to agricultural extension officers for crop diagnosis, weather advisories, market rates, and government schemes in 22 local languages.",
            kcc_hours: "Operating Hours: 6:00 AM to 10:00 PM (All 7 Days) · IVRS available 24/7",
            kcc_advisory: "Note: Farmers should confirm current service availability and language options through official sources.",
            kcc_action: "Call Toll-Free 1800-180-1551",
            when_title: "When to Consult an Agricultural Expert",
            when_desc: "While AI visual diagnosis provides rapid initial screening, you should contact your local KVK or Agriculture Officer in these situations:",
            when1_title: "1. Uncertain Visual Diagnosis (< 50% Confidence)",
            when1_desc: "When visual symptoms overlap among multiple diseases or confidence is low, laboratory inspection or field examination is essential before taking corrective action.",
            when2_title: "2. Worsening or Rapidly Spreading Symptoms",
            when2_desc: "If leaf lesions, wilting, or yellowing spreads quickly across your field despite initial sanitation or cultural measures.",
            when3_title: "3. Recurring Disease Outbreaks / Soil Issues",
            when3_desc: "If the disease reappears in successive seasons, suggesting soil-borne pathogens, resistant strains, or micronutrient deficiencies.",
            when4_title: "4. Chemical Treatment & Fungicide Decisions",
            when4_desc: "Never apply chemical fungicides, insecticides, or restricted formulations without confirming the target pathogen, label dose, waiting periods, and safety intervals.",
            institutions_title: "Established Agricultural Extension Institutions in India",
            institutions_desc: "Official government and academic bodies providing verified diagnostic and advisory support to Indian farmers:",
            kvk_title: "Krishi Vigyan Kendras (KVKs)",
            kvk_desc: "Network of 730+ ICAR agricultural science centres located in nearly every rural district of India. Provides hands-on crop diagnosis, soil testing, and technology demonstration.",
            dept_title: "State Agriculture Departments & Krishi Bhavans",
            dept_desc: "District Agriculture Officers (DAO) and Block-level Agriculture Development Officers (ADO) providing field inspections, input subsidy verification, and subsidized pest control.",
            univ_title: "Agricultural Universities (SAUs) & ICAR Institutes",
            univ_desc: "State Agricultural Universities and national research institutes offering specialized plant pathology clinics, diagnostic laboratories, and crop management guidelines.",
            location_label: "Find Your District KVK & Extension Office:",
            location_placeholder: "Enter state, district, city, or PIN code (e.g. Pune, Karnal, Guntur, 522002)...",
            search_btn: "🔍 Find Local KVK / Office",
            detect_btn: "🎯 Use My Location (Optional)",
            results_for: "Agricultural Extension & KVK Options for:",
            summary_title: "Farmer Consultation Summary Generator",
            summary_desc: "Generate a structured consultation summary from your visual diagnosis to share with a KVK scientist or Agriculture Extension Officer over WhatsApp, SMS, or printout.",
            crop_label: "Crop Name:",
            disease_label: "Visual Diagnosis / Suspected Disease:",
            confidence_label: "Visual Confidence Level:",
            symptoms_label: "Observed Leaf & Field Symptoms (Your Notes):",
            symptoms_placeholder: "e.g., Small dark circular spots with concentric rings on lower leaves, noticed 3 days ago after rain...",
            severity_label: "Severity / Extent of Damage:",
            severity_opt1: "Low (Few leaves / isolated plants)",
            severity_opt2: "Moderate (10% - 25% of crop affected)",
            severity_opt3: "Severe (> 25% of field affected / spreading fast)",
            generate_btn: "📝 Update Consultation Summary",
            copy_btn: "📋 Copy Summary for Expert",
            copied_text: "✓ Consultation summary copied to clipboard! Ready to share.",
            preview_title: "Consultation Summary Preview",
            auto_loaded_note: "✓ Pre-filled from your most recent crop visual diagnosis on this device."
        },
        about: {
            section_label: "HOW IT WORKS",
            title: "How CropCure AI Works",
            stage1_title: "1. Upload Image",
            stage1_desc: "Take or select a clear photo of an affected crop leaf using your mobile or computer.",
            stage2_title: "2. CNN Diagnosis",
            stage2_desc: "Our trained Convolutional Neural Network evaluates the leaf visual pattern and computes confidence across candidate disease classes.",
            stage3_title: "3. Knowledge Retrieval",
            stage3_desc: "The FAISS retriever queries the agricultural knowledge base to find verified symptoms, treatment, and preventive measures.",
            stage4_title: "4. AI Guidance",
            stage4_desc: "The Groq LLM synthesizes a grounded, farmer-friendly response strictly adhering to retrieved facts without hallucinations."
        },
        crops: {
            Apple: "Apple",
            Corn: "Corn (Maize)",
            Potato: "Potato",
            Tomato: "Tomato",
            Grape: "Grape"
        },
        diseases: {
            Apple_Healthy: "Apple (Healthy)",
            Apple_Rust: "Apple Rust",
            Apple_Scab: "Apple Scab",
            Corn_Gray_Leaf_Spot: "Corn Gray Leaf Spot",
            Corn_Leaf_Blight: "Corn Leaf Blight",
            Corn_Leaf_Rust: "Corn Leaf Rust",
            Potato_Early_Blight: "Potato Early Blight",
            Potato_Late_Blight: "Potato Late Blight",
            Potato_Leaf_Blight: "Potato Leaf Blight",
            Potato_Leafroll_Virus: "Potato Leafroll Virus",
            Potato_Healthy: "Potato (Healthy)",
            Tomato_Bacterial_Spot: "Tomato Bacterial Spot",
            Tomato_Early_Blight: "Tomato Early Blight",
            Tomato_Late_Blight: "Tomato Late Blight",
            Tomato_Leaf_Mold: "Tomato Leaf Mold",
            Tomato_Septoria_Leaf_Spot: "Tomato Septoria Leaf Spot",
            Tomato_Healthy: "Tomato (Healthy)",
            Grape_Black_Rot: "Grape Black Rot"
        }
    },

    te: {
        nav: {
            brand: "క్రాప్‌క్యూర్ AI",
            home: "హోమ్",
            diagnosis: "వ్యాధి నిర్ధారణ",
            schemes: "ప్రభుత్వ పథకాలు",
            shops: "సమీప దుకాణాలు",
            experts: "వ్యవసాయ నిపుణులు",
            performance: "మోడల్ పనితీరు",
            chat: "AI సహాయకుడు",
            about: "విధానం"
        },
        common: {
            tagline: "AI-ఆధారిత పంట ఆరోగ్యం",
            copyright: "© 2026 క్రాప్‌క్యూర్ AI. అకడమిక్ ప్రాజెక్ట్.",
            clear: "క్లియర్",
            loading: "లోడ్ అవుతోంది...",
            search: "వెతకండి",
            all: "అన్నీ",
            retry: "మళ్లీ ప్రయత్నించండి",
            optional: "ఐచ్ఛికం",
            disclaimer: "గమనిక / నిరాకరణ",
            official_portal: "అధికారిక పోర్టల్ సందర్శించండి ↗",
            open_in_maps: "గూగుల్ మ్యాప్స్‌లో తెరవండి ↗",
            open_in_osm: "ఓపెన్‌స్ట్రీట్‌మ్యాప్‌లో తెరవండి ↗",
            get_directions: "దారి దిశలు పొందండి ↗",
            verified: "ధృవీకరించబడింది",
            verified_badge: "✓ ధృవీకరించబడిన కేంద్ర పథకం",
            footer_desc: "భారతీయ రైతుల కోసం ఏఐ-ఆధారిత పంట తెగుళ్ల గుర్తింపు మరియు వ్యవసాయ సహాయం."
        },
        hero: {
            title_prefix: "స్మార్ట్ పంట తెగుళ్ల",
            title_highlight: "నిర్ధారణ",
            description: "పంట ఆకు ఫోటోను అప్‌లోడ్ చేయండి. క్రాప్‌క్యూర్ AI డీప్ లెర్నింగ్ ద్వారా విశ్లేషించి, తగిన నివారణ మరియు సంరక్షణ మార్గదర్శకాలను అందిస్తుంది.",
            start_button: "వ్యాధి నిర్ధారణ ప్రారంభించండి"
        },
        diagnosis: {
            section_label: "తెగుళ్ల గుర్తింపు",
            title: "మీ పంటను విశ్లేషించండి",
            description: "సాధ్యమయ్యే తెగుళ్లను గుర్తించడానికి పంట ఆకు యొక్క స్పష్టమైన చిత్రాన్ని అప్‌లోడ్ చేయండి.",
            upload_title: "ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి",
            upload_desc: "వ్యాధి సోకిన మొక్క ఆకు స్పష్టమైన చిత్రాన్ని ఎంచుకోండి. ఫార్మాట్‌లు: JPG, PNG, WEBP.",
            choose_image: "ఆకు ఫోటోను ఎంచుకోండి",
            analyze_button: "వ్యాధిని విశ్లేషించండి",
            analyzing_button: "చిత్రాన్ని విశ్లేషిస్తోంది...",
            result_label: "నిర్ధారణ నివేదిక",
            primary_title: "ప్రాథమిక దృశ్య నిర్ధారణ",
            uncertain_title: "దృశ్య నిర్ధారణ (అనిశ్చితం)",
            uncertain_badge: "అనిశ్చిత నిర్ధారణ (< 50%)",
            low_conf_badge: "తక్కువ ఖచ్చితత్వం",
            high_conf_badge: "అధిక ఖచ్చితత్వం",
            confidence_label: "ఖచ్చితత్వ స్థాయి",
            uncertain_warning_title: "⚠️ అనిశ్చిత దృశ్య నిర్ధారణ (< 50% ఖచ్చితత్వం)",
            uncertain_warning_desc: "దృశ్య నిర్ధారణ అనిశ్చితంగా ఉంది. మోడల్ బహుళ అవకాశాలను గుర్తించింది. చర్య తీసుకునే ముందు అభ్యర్థి లక్షణాలను సరిపోల్చండి.",
            top3_title: "ప్రధాన ప్రత్యామ్నాయ అభ్యర్థులు (టాప్ 3)",
            top3_subtitle: "చికిత్స చర్యలు చేపట్టే ముందు ఈ అభ్యర్థుల లక్షణాలను సరిపోల్చండి:",
            no_knowledge: "ప్రస్తుత డేటాబేస్‌లో ఈ వ్యాధికి వ్యవసాయ సమాచారం అందుబాటులో లేదు.",
            view_details: "లక్షణాలు & సలహాలను సరిపోల్చండి"
        },
        cards: {
            symptoms_title: "వ్యాధి లక్షణాలు (Symptoms)",
            treatment_title: "సిఫార్సు చేసిన చికిత్స (Treatment)",
            prevention_title: "నివారణ చర్యలు (Prevention)",
            guidance_title: "AI వ్యవసాయ మార్గదర్శకత్వం",
            ask_title: "ఈ వ్యాధి గురించి ప్రశ్న అడగండి",
            ask_placeholder: "సేంద్రీయ నివారణలు, స్ప్రే సమయం లేదా లక్షణాల గురించి అడగండి...",
            ask_button: "సలహా పొందండి"
        },
        chat: {
            section_label: "RAG & LLM సహాయం",
            title: "AI వ్యవసాయ సహాయకుడు",
            description: "పంట తెగుళ్లు, సేంద్రీయ సంరక్షణ, ప్రభుత్వ పథకాలు లేదా వ్యవసాయ నిర్వహణ గురించి ప్రశ్నలు అడగండి.",
            welcome_msg: "నమస్కారం! నేను మీ క్రాప్‌క్యూర్ AI వ్యవసాయ సహాయకుడిని. మీరు పంట తెగుళ్లు, లక్షణాలు, చికిత్స, సేంద్రీయ పద్ధతులు మరియు ప్రభుత్వ పథకాల గురించి తెలుగు, హిందీ లేదా ఇంగ్లీషులో నన్ను అడగవచ్చు.",
            placeholder: "మీ వ్యవసాయ ప్రశ్నను ఇక్కడ టైప్ చేయండి (తెలుగు, హిందీ లేదా ఇంగ్లీషులో)...",
            send_button: "పంపండి",
            empty_error: "దయచేసి పంపే ముందు ఒక ప్రశ్నను నమోదు చేయండి."
        },
        schemes: {
            section_label: "భారత ప్రభుత్వ కార్యక్రమాలు",
            title: "ప్రభుత్వ వ్యవసాయ పథకాలు & సబ్సిడీలు",
            description: "భారతీయ రైతుల కోసం ధృవీకరించబడిన కేంద్ర పథకాలు, ఆర్థిక సహాయం, పంట బీమా, సూక్ష్మ నీటిపారుదల సబ్సిడీలు మరియు సహాయక సేవలను తెలుసుకోండి.",
            banner_title: "ధృవీకరించబడిన అధికారిక పోర్టల్స్ డైరెక్టరీ",
            banner_badge: "ధృవీకరించబడింది · అక్టోబర్ 2026",
            banner_text: "ఈ డైరెక్టరీ రైతుల సమాచారం కోసం భారత ప్రభుత్వ అధికారిక పోర్టల్స్ నుండి సేకరించిన ప్రామాణిక వ్యవసాయ పథకాలను అందిస్తుంది.",
            helpline_title: "రైతు ఉచిత హెల్ప్‌లైన్ నంబర్లు:",
            search_placeholder: "పథకం పేరు లేదా కీవర్డ్ ద్వారా వెతకండి (ఉదా: బీమా, సబ్సిడీ, రుణం, విత్తనాలు, డ్రిప్)...",
            showing_text: "చూపిస్తున్నవి",
            verified_count_text: "ధృవీకరించబడిన ప్రభుత్వ పథకాలు",
            benefits_heading: "ప్రధాన ప్రయోజనాలు & ఆర్థిక సహాయం",
            eligibility_heading: "అర్హత వివరాలు",
            steps_heading: "దరఖాస్తు చేసుకునే విధానం (ధృవీకరించబడిన దశలు)",
            empty_title: "పథకాలు కనుగొనబడలేదు",
            empty_desc: "మీ శోధన కీవర్డ్ లేదా వర్గానికి సరిపోలే వ్యవసాయ పథకాలు ఏవీ లభించలేదు.",
            reset_filters: "అన్ని ఫిల్టర్‌లను రీసెట్ చేయండి"
        },
        shops: {
            section_label: "స్థానిక వ్యవసాయ సరఫరాలు",
            title: "సమీప వ్యవసాయ సరఫరా దుకాణాలు",
            description: "మీ ప్రాంతంలో ధృవీకరించబడిన విత్తనాలు, ఎరువులు, పంట రక్షణ మందులు మరియు వ్యవసాయ పరికరాల దుకాణాలను కనుగొనండి.",
            banner_title: "బాహ్య మ్యాప్స్ సేవ & వ్యవసాయ భద్రతా గమనిక",
            banner_text: "క్రాప్‌క్యూర్ AI గూగుల్ మ్యాప్స్ మరియు ఓపెన్‌స్ట్రీట్‌మ్యాప్స్ ద్వారా నిజమైన దుకాణాల లొకేషన్లు మరియు దారి దిశలను సులభంగా చూపిస్తుంది.",
            location_label: "1. మీ ప్రాంతాన్ని నమోదు చేయండి (నగరం, గ్రామం లేదా పిన్ కోడ్):",
            location_placeholder: "ఉదా: Pune, 411001, Guntur, Vijayawada, Kurnool...",
            detect_btn: "🎯 నా స్థానాన్ని గుర్తించండి (ఐచ్ఛికం)",
            find_btn: "🔍 సమీప దుకాణాలను కనుగొనండి",
            category_label: "2. సరఫరా వర్గాన్ని ఎంచుకోండి:",
            results_for: "వ్యవసాయ దుకాణ ఎంపికలు:",
            supply_grid_heading: "మీ ప్రాంతంలోని సరఫరా వర్గాలు",
            tips_title: "రైతు సూచనలు: వ్యవసాయ సామాగ్రి కొనుగోలు చేసేటప్పుడు గమనించవలసినవి",
            prompt_title: "ధృవీకరించబడిన వ్యవసాయ డీలర్లను కనుగొనండి",
            prompt_desc: "పైన మీ పట్టణం, గ్రామం లేదా పిన్ కోడ్‌ను నమోదు చేసి 'సమీప దుకాణాలను కనుగొనండి' క్లిక్ చేయండి."
        },
        experts: {
            section_label: "సంస్థాగత విస్తరణ & శాస్త్రీయ సలహా",
            title: "వ్యవసాయ నిపుణుల మద్దతు & విస్తరణ సేవలు",
            description: "భారతదేశం అంతటా సర్టిఫైడ్ వ్యవసాయ శాస్త్రవేత్తలు, కృషి విజ్ఞాన కేంద్రాలు (KVKs) మరియు ప్రభుత్వ వ్యవసాయ అధికారులతో సంప్రదించండి.",
            banner_title: "అధికారిక వ్యవసాయ సలహా & ప్రాథమిక అంచనా గమనిక",
            banner_text: "క్రాప్‌క్యూర్ AI ప్రాథమిక కంప్యూటర్ దృష్టి విశ్లేషణను అందిస్తుంది. ప్రత్యేకంగా రసాయన మందులు వాడే ముందు, శాస్త్రవేత్తల ప్రత్యక్ష పంట పరిశీలన అత్యంత ఆవశ్యకం.",
            kcc_title: "జాతీయ కిసాన్ కాల్ సెంటర్ (టోల్-ఫ్రీ హాట్‌లైన్)",
            kcc_number: "1800-180-1551",
            kcc_desc: "22 స్థానిక భాషలలో పంట రోగ నిర్ధారణ, వాతావరణ సలహాలు మరియు ప్రభుత్వ పథకాలపై సమాచారం అందించే ఉచిత టెలిఫోన్ సేవ.",
            kcc_hours: "పని వేళలు: ఉదయం 6:00 నుండి రాత్రి 10:00 వరకు (వారంలో అన్ని రోజులు) · IVRS 24/7 అందుబాటులో ఉంటుంది",
            kcc_advisory: "గమనిక: రైతులు ప్రస్తుత సేవా లభ్యత మరియు భాషా ఎంపికలను అధికారిక మూలాల ద్వారా ధృవీకరించుకోవాలి.",
            kcc_action: "ఉచిత కాల్ చేయండి: 1800-180-1551",
            when_title: "వ్యవసాయ నిపుణుడిని ఎప్పుడు సంప్రదించాలి?",
            when_desc: "AI దృశ్య నిర్ధారణ ప్రాథమిక స్క్రీనింగ్ అందిస్తున్నప్పటికీ, ఈ క్రింది పరిస్థితులలో మీ స్థానిక KVK లేదా వ్యవసాయ అధికారిని తప్పక సంప్రదించాలి:",
            when1_title: "1. అనిశ్చిత దృశ్య నిర్ధారణ (< 50% విశ్వసనీయత)",
            when1_desc: "లక్షణాలు బహుళ తెగుళ్ళ మధ్య పోలిక కలిగి ఉన్నప్పుడు లేదా విశ్వసనీయత తక్కువగా ఉన్నప్పుడు, నిపుణుల ప్రత్యక్ష పరిశీలన అవసరం.",
            when2_title: "2. వేగంగా వ్యాపించే లేదా తీవ్రమవుతున్న తెగులు",
            when2_desc: "ప్రాథమిక నివారణ చర్యలు చేపట్టినప్పటికీ ఆకులు ఎండిపోవడం లేదా పసుపు రంగులోకి మారడం వేగంగా పెరుగుతుంటే.",
            when3_title: "3. పదేపదే వచ్చే తెగుళ్ళు / నేల సమస్యలు",
            when3_desc: "ప్రతి పంట సీజన్‌లో తెగులు పునరావృతమైతే, నేల ద్వారా వ్యాపించే శిలీంధ్రాలు లేదా పోషక లోపాలు కారణం కావచ్చు.",
            when4_title: "4. రసాయన మందులు & పురుగుమందుల వాడకం",
            when4_desc: "నిర్దిష్ట తెగులు నిర్ధారణ, సరైన మోతాదు మరియు రక్షణ వ్యవధి తెలియకుండా రసాయన మందులను ఎప్పుడూ పిచికారీ చేయవద్దు.",
            institutions_title: "భారతదేశంలోని ప్రముఖ వ్యవసాయ విస్తరణ సంస్థలు",
            institutions_desc: "రైతులకు నమ్మకమైన శాస్త్రీయ సలహాలు అందించే అధికారిక ప్రభుత్వ మరియు విశ్వవిద్యాలయ విభాగాలు:",
            kvk_title: "కృషి విజ్ఞాన కేంద్రాలు (KVKs)",
            kvk_desc: "భారతదేశంలోని దాదాపు ప్రతి జిల్లాలో ఉన్న 730+ ICAR వ్యవసాయ విజ్ఞాన కేంద్రాలు. పంట వ్యాధి నిర్ధారణ, నేల పరీక్షలు మరియు సాంకేతిక ప్రదర్శనలను అందిస్తాయి.",
            dept_title: "రాష్ట్ర వ్యవసాయ శాఖ & రైతు సేవా కేంద్రాలు",
            dept_desc: "క్షేత్ర స్థాయి పరిశీలనలు, ఎరువుల రాయితీలు మరియు తెగుళ్ళ నివారణకు సహాయపడే జిల్లా మరియు మండల స్థాయి వ్యవసాయ అధికారులు (ADA/AO).",
            univ_title: "వ్యవసాయ విశ్వవిద్యాలయాలు & ICAR పరిశోధనా సంస్థలు",
            univ_desc: "ప్రత్యేక ప్లాంట్ పాథాలజీ క్లినిక్‌లు, రోగ నిర్ధారణ ప్రయోగశాలలు మరియు శాస్త్రీయ సలహాలను అందించే పరిశోధనా సంస్థలు.",
            location_label: "మీ జిల్లా KVK & వ్యవసాయ కార్యాలయాన్ని కనుగొనండి:",
            location_placeholder: "రాష్ట్రం, జిల్లా, పట్టణం లేదా పిన్ కోడ్ నమోదు చేయండి (ఉదా: Guntur, Vijayawada, Kurnool, 522002)...",
            search_btn: "🔍 స్థానిక KVK / కార్యాలయాన్ని కనుగొనండి",
            detect_btn: "🎯 నా స్థానాన్ని గుర్తించండి (ఐచ్ఛికం)",
            results_for: "వ్యవసాయ విస్తరణ & KVK ఎంపికలు:",
            summary_title: "రైతు సంప్రదింపు సారాంశ జనరేటర్",
            summary_desc: "KVK శాస్త్రవేత్త లేదా వ్యవసాయ అధికారితో WhatsApp, SMS ద్వారా పంచుకోవడానికి మీ పంట రోగ నిర్ధారణ సారాంశాన్ని రూపొందించండి.",
            crop_label: "పంట పేరు:",
            disease_label: "దృశ్య నిర్ధారణ / అనుమానిత వ్యాధి:",
            confidence_label: "విశ్వసనీయత స్థాయి:",
            symptoms_label: "గమనించిన ఆకు & పొలం లక్షణాలు (మీ గమనికలు):",
            symptoms_placeholder: "ఉదా: ఆకుల అడుగున నల్లటి వలయాకార మచ్చలు, 3 రోజుల క్రితం వర్షం తర్వాత గమనించాను...",
            severity_label: "నష్టం తీవ్రత / వ్యాప్తి:",
            severity_opt1: "తక్కువ (కొన్ని ఆకులు / చెదురుమదురు మొక్కలు)",
            severity_opt2: "మధ్యస్థం (పంటలో 10% - 25% వరకు నష్టం)",
            severity_opt3: "తీవ్రం (> 25% పొలం ప్రభావితమైంది / వేగంగా వ్యాపిస్తోంది)",
            generate_btn: "📝 సంప్రదింపు సారాంశాన్ని నవీకరించండి",
            copy_btn: "📋 నిపుణుడి కోసం సారాంశాన్ని కాపీ చేయండి",
            copied_text: "✓ సారాంశం క్లిప్‌బోర్డ్‌కు కాపీ చేయబడింది! షేర్ చేయడానికి సిద్ధంగా ఉంది.",
            preview_title: "సంప్రదింపు సారాంశ ప్రివ్యూ",
            auto_loaded_note: "✓ మీ ఇటీవలి పంట నిర్ధారణ నుండి స్వయంచాలకంగా పూరించబడింది."
        },
        about: {
            section_label: "కార్యవిధానం",
            title: "క్రాప్‌క్యూర్ AI ఎలా పనిచేస్తుంది",
            stage1_title: "1. చిత్రం అప్‌లోడ్",
            stage1_desc: "మీ మొబైల్ లేదా కంప్యూటర్ ఉపయోగించి తెగులు సోకిన పంట ఆకు యొక్క స్పష్టమైన ఫోటోను ఎంచుకోండి.",
            stage2_title: "2. CNN రోగ నిర్ధారణ",
            stage2_desc: "మా శిక్షణ పొందిన CNN మోడల్ ఆకు దృశ్య లక్షణాలను విశ్లేషించి, సంభావ్య వ్యాధి తరగతులను గణిస్తుంది.",
            stage3_title: "3. సమాచార సేకరణ (RAG)",
            stage3_desc: "FAISS రిట్రీవర్ వ్యవసాయ డేటాబేస్ నుండి ధృవీకరించబడిన లక్షణాలు, చికిత్స మరియు నివారణ చర్యలను పొందుతుంది.",
            stage4_title: "4. AI మార్గదర్శకత్వం",
            stage4_desc: "Groq LLM ఆధారిత వ్యవస్థ సేకరించిన సమాచారానికి మాత్రమే కట్టుబడి సులభమైన రైతు సలహాలను రూపొందిస్తుంది."
        },
        crops: {
            Apple: "యాపిల్",
            Corn: "మొక్కజొన్న",
            Potato: "బంగాళాదుంప",
            Tomato: "టమాటా",
            Grape: "ద్రాక్ష"
        },
        diseases: {
            Apple_Healthy: "యాపిల్ (ఆరోగ్యకరమైనది)",
            Apple_Rust: "యాపిల్ తుప్పు తెగులు",
            Apple_Scab: "యాపిల్ స్కాబ్ తెగులు",
            Corn_Gray_Leaf_Spot: "మొక్కజొన్న బూడిద రంగు ఆకుమచ్చ తెగులు",
            Corn_Leaf_Blight: "మొక్కజొన్న ఆకు ఎండు తెగులు (బ్లైట్)",
            Corn_Leaf_Rust: "మొక్కజొన్న ఆకు తుప్పు తెగులు",
            Potato_Early_Blight: "బంగాళాదుంప ఎర్లీ బ్లైట్ తెగులు",
            Potato_Late_Blight: "బంగాళాదుంప లేట్ బ్లైట్ తెగులు",
            Potato_Leaf_Blight: "బంగాళాదుంప ఆకు ఎండు తెగులు",
            Potato_Leafroll_Virus: "బంగాళాదుంప ఆకు చుట్ట వైరస్ తెగులు",
            Potato_Healthy: "బంగాళాదుంప (ఆరోగ్యకరమైనది)",
            Tomato_Bacterial_Spot: "టమాటా బ్యాక్టీరియల్ మచ్చ తెగులు",
            Tomato_Early_Blight: "టమాటా ఎర్లీ బ్లైట్ (ముందస్తు మచ్చ) తెగులు",
            Tomato_Late_Blight: "టమాటా లేట్ బ్లైట్ తెగులు",
            Tomato_Leaf_Mold: "టమాటా ఆకు బూజు తెగులు",
            Tomato_Septoria_Leaf_Spot: "టమాటా సెప్టోరియా ఆకుమచ్చ తెగులు",
            Tomato_Healthy: "టమాటా (ఆరోగ్యకరమైనది)",
            Grape_Black_Rot: "ద్రాక్ష నల్ల కుళ్ళు తెగులు"
        }
    },

    hi: {
        nav: {
            brand: "क्रॉपक्योर AI",
            home: "होम",
            diagnosis: "रोग निदान",
            schemes: "सरकारी योजनाएं",
            shops: "नजदीकी दुकानें",
            experts: "कृषि विशेषज्ञ",
            performance: "मॉडल प्रदर्शन",
            chat: "एआई सहायक",
            about: "परिचय"
        },
        common: {
            tagline: "एआई-संचालित फसल स्वास्थ्य",
            copyright: "© 2026 क्रॉपक्योर AI. शैक्षणिक परियोजना।",
            clear: "हटाएं",
            loading: "लोड हो रहा है...",
            search: "खोजें",
            all: "सभी",
            retry: "पुनः प्रयास करें",
            optional: "वैकल्पिक",
            disclaimer: "अस्वीकरण / सूचना",
            official_portal: "आधिकारिक पोर्टल पर जाएं ↗",
            open_in_maps: "गूगल मैप्स में खोलें ↗",
            open_in_osm: "ओपनस्ट्रीटमैप में खोलें ↗",
            get_directions: "दिशा-निर्देश प्राप्त करें ↗",
            verified: "सत्यापित",
            verified_badge: "✓ सत्यापित केंद्रीय योजना",
            footer_desc: "भारतीय किसानों के लिए एआई-संचालित फसल रोग पहचान और कृषि सहायता।"
        },
        hero: {
            title_prefix: "स्मार्ट फसल रोग",
            title_highlight: "निदान",
            description: "फसल की पत्ती की तस्वीर अपलोड करें और क्रॉपक्योर AI द्वारा डीप लर्निंग के जरिए रोग विश्लेषण, उपचार व बचाव मार्गदर्शन प्राप्त करें।",
            start_button: "रोग निदान शुरू करें"
        },
        diagnosis: {
            section_label: "रोग पहचान",
            title: "अपनी फसल का विश्लेषण करें",
            description: "संभावित रोगों की पहचान के लिए फसल की पत्ती की स्पष्ट तस्वीर अपलोड करें।",
            upload_title: "पत्ती की फोटो अपलोड करें",
            upload_desc: "संक्रमित पौधे की पत्ती की स्पष्ट फोटो चुनें। प्रारूप: JPG, PNG, WEBP.",
            choose_image: "पत्ती की फोटो चुनें",
            analyze_button: "रोग का विश्लेषण करें",
            analyzing_button: "विश्लेषण जारी है...",
            result_label: "निदान रिपोर्ट",
            primary_title: "प्राथमिक दृश्य निदान",
            uncertain_title: "दृश्य निदान (अनिश्चित)",
            uncertain_badge: "अनिश्चित निदान (< 50%)",
            low_conf_badge: "कम सटीकता",
            high_conf_badge: "उच्च सटीकता",
            confidence_label: "सटीकता स्तर",
            uncertain_warning_title: "⚠️ अनिश्चित दृश्य निदान (< 50% विश्वास)",
            uncertain_warning_desc: "दृश्य निदान अनिश्चित है। मॉडल ने कई संभावित विकल्पों की पहचान की है। उपचार करने से पहले लक्षणों की पुष्टि करें।",
            top3_title: "शीर्ष संभावित विकल्प (Top-3 Candidates)",
            top3_subtitle: "उपचार कदम उठाने से पहले इन संभावित रोगों के लक्षणों की तुलना करें:",
            no_knowledge: "वर्तमान डेटाबेस में इस रोग के लिए विशिष्ट कृषि जानकारी उपलब्ध नहीं है।",
            view_details: "लक्षण व परामर्श की तुलना करें"
        },
        cards: {
            symptoms_title: "रोग के लक्षण (Symptoms)",
            treatment_title: "अनुशंसित उपचार (Treatment)",
            prevention_title: "बचाव के उपाय (Prevention)",
            guidance_title: "एआई कृषि परामर्श",
            ask_title: "इस निदान के बारे में प्रश्न पूछें",
            ask_placeholder: "जैविक उपचार, दवा छिड़काव समय या लक्षणों के बारे में पूछें...",
            ask_button: "परामर्श लें"
        },
        chat: {
            section_label: "RAG एवं LLM परामर्श",
            title: "एआई कृषि सहायक",
            description: "फसल रोगों, जैविक देखभाल, सरकारी योजनाओं या कृषि प्रबंधन से संबंधित प्रश्न पूछें।",
            welcome_msg: "नमस्ते! मैं आपका क्रॉपक्योर AI कृषि सहायक हूँ। आप मुझसे फसल रोगों, लक्षणों, उपचार, जैविक खेती और सरकारी योजनाओं के बारे में हिंदी, तेलुगु या अंग्रेजी में पूछ सकते हैं।",
            placeholder: "अपना कृषि प्रश्न यहाँ लिखें (हिंदी, तेलुगु या अंग्रेजी में)...",
            send_button: "भेजें",
            empty_error: "कृपया भेजने से पहले एक प्रश्न लिखें।"
        },
        schemes: {
            section_label: "भारत सरकार की पहल",
            title: "सरकारी कृषि योजनाएं एवं सब्सिडी",
            description: "भारतीय किसानों के लिए सत्यापित केंद्रीय कृषि योजनाएं, वित्तीय सहायता, फसल बीमा, सूक्ष्म सिंचाई सब्सिडी और कृषि सहायता सेवाएं जानें।",
            banner_title: "सत्यापित आधिकारिक पोर्टल निर्देशिका",
            banner_badge: "सत्यापित · अक्टूबर 2026",
            banner_text: "यह निर्देशिका आधिकारिक भारत सरकार पोर्टलों से किसानों की सहायता के लिए प्रामाणिक कृषि योजनाओं का संकलन प्रस्तुत करती है।",
            helpline_title: "किसान टोल-फ्री हेल्पलाइन नंबर:",
            search_placeholder: "योजना का नाम या कीवर्ड खोजें (उदा: बीमा, सब्सिडी, ऋण, बीज, ड्रिप)...",
            showing_text: "दिखाई जा रही हैं",
            verified_count_text: "सत्यापित सरकारी योजनाएं",
            benefits_heading: "प्रमुख लाभ एवं वित्तीय सहायता",
            eligibility_heading: "पात्रता सारांश",
            steps_heading: "आवेदन कैसे करें (सत्यापित चरण)",
            empty_title: "कोई योजना नहीं मिली",
            empty_desc: "आपके खोज कीवर्ड या श्रेणी फ़िल्टर से मेल खाती कोई कृषि योजना नहीं मिली।",
            reset_filters: "सभी फ़िल्टर रीसेट करें"
        },
        shops: {
            section_label: "स्थानीय कृषि आपूर्ति",
            title: "नजदीकी कृषि इनपुट दुकानें",
            description: "अपने क्षेत्र में प्रमाणित बीज, उर्वरक, फसल सुरक्षा रसायन और कृषि उपकरण विक्रेता खोजें।",
            banner_title: "बाहरी मानचित्र सेवा एवं कृषि सुरक्षा सूचना",
            banner_text: "क्रॉपक्योर AI गूगल मैप्स और ओपनस्ट्रीटमैप के माध्यम से दुकानों के सटीक स्थान और दिशा-निर्देश प्रदान करता है।",
            location_label: "1. अपना स्थान दर्ज करें (शहर, कस्बा, गांव या पिन कोड):",
            location_placeholder: "उदा: Pune, 411001, Karnal, Lucknow, Patna...",
            detect_btn: "🎯 मेरी लोकेशन का उपयोग करें (वैकल्पिक)",
            find_btn: "🔍 नजदीकी दुकानें खोजें",
            category_label: "2. आपूर्ति श्रेणी चुनें:",
            results_for: "कृषि इनपुट आपूर्ति विकल्प:",
            supply_grid_heading: "आपके क्षेत्र में आपूर्ति श्रेणियां",
            tips_title: "किसान परामर्श: कृषि सामग्री खरीदते समय ध्यान रखने योग्य बातें",
            prompt_title: "सत्यापित कृषि इनपुट विक्रेता खोजें",
            prompt_desc: "ऊपर अपना शहर, गांव या पिन कोड दर्ज करें और 'नजदीकी दुकानें खोजें' पर क्लिक करें।"
        },
        experts: {
            section_label: "संस्थागत विस्तार एवं वैज्ञानिक परामर्श",
            title: "कृषि विशेषज्ञ सहायता एवं विस्तार सेवाएं",
            description: "संपूर्ण भारत में प्रमाणित कृषि वैज्ञानिकों, कृषि विज्ञान केंद्रों (KVKs) और सरकारी कृषि विस्तार अधिकारियों से संपर्क करें।",
            banner_title: "आधिकारिक कृषि परामर्श एवं प्रारंभिक पूर्वानुमान सूचना",
            banner_text: "क्रॉपक्योर AI कंप्यूटर विज़न आधारित प्रारंभिक अनुमान प्रदान करता है। मशीन लर्निंग पूर्वानुमान कभी भी प्रमाणित कृषि वैज्ञानिकों द्वारा वास्तविक खेत निरीक्षण का विकल्प नहीं हो सकते, विशेषकर रासायनिक उपचार से पूर्व।",
            kcc_title: "राष्ट्रीय किसान कॉल सेंटर (टोल-फ्री हेल्पलाइन)",
            kcc_number: "1800-180-1551",
            kcc_desc: "22 स्थानीय भाषाओं में फसल रोग निदान, मौसम परामर्श, मंडी भाव और सरकारी योजनाओं पर सीधे कृषि विशेषज्ञों से बात करने की सुविधा।",
            kcc_hours: "कार्य समय: सुबह 6:00 से रात 10:00 बजे तक (सप्ताह के सातों दिन) · IVRS सुविधा 24/7",
            kcc_advisory: "नोट: किसान भाई आधिकारिक स्रोतों से वर्तमान सेवा उपलब्धता और भाषा विकल्पों की पुष्टि कर लें।",
            kcc_action: "टोल-फ्री कॉल करें: 1800-180-1551",
            when_title: "कृषि विशेषज्ञ से कब संपर्क करें?",
            when_desc: "यद्यपि एआई दृश्य निदान त्वरित प्रारंभिक जांच प्रदान करता है, निम्नलिखित स्थितियों में अपने नजदीकी KVK या कृषि अधिकारी से तुरंत संपर्क करें:",
            when1_title: "1. अनिश्चित दृश्य निदान (< 50% विश्वसनीयता)",
            when1_desc: "जब लक्षण कई रोगों के बीच मिलते-जुलते हों या विश्वसनीयता कम हो, तब कोई भी कदम उठाने से पहले विशेषज्ञ से प्रत्यक्ष जांच जरूरी है।",
            when2_title: "2. तेजी से बढ़ते या गंभीर होते लक्षण",
            when2_desc: "यदि प्रारंभिक उपायों के बावजूद पत्तों पर धब्बे, झुलसा या पीलापन खेत में तेजी से फैल रहा हो।",
            when3_title: "3. बार-बार होने वाले रोग / मिट्टी जनित समस्याएं",
            when3_desc: "यदि हर मौसम में वही रोग दोबारा प्रकट होता है, जो मिट्टी जनित रोगजनकों या पोषक तत्वों की कमी का संकेत हो सकता है।",
            when4_title: "4. रासायनिक कीटनाशक व फफूंदनाशक निर्णय",
            when4_desc: "सटीक रोग पहचान, अनुशंसित खुराक, छिड़काव अंतराल और प्रतीक्षा अवधि की पुष्टि किए बिना रसायनों का प्रयोग कभी न करें।",
            institutions_title: "भारत में स्थापित कृषि विस्तार संस्थान",
            institutions_desc: "भारतीय किसानों को प्रामाणिक वैज्ञानिक एवं नैदानिक परामर्श प्रदान करने वाले आधिकारिक सरकारी संस्थान:",
            kvk_title: "कृषि विज्ञान केंद्र (KVKs)",
            kvk_desc: "भारत के लगभग हर ग्रामीण जिले में स्थित 730+ ICAR कृषि विज्ञान केंद्रों का नेटवर्क। प्रत्यक्ष रोग निदान, मिट्टी परीक्षण और तकनीकी प्रदर्शन प्रदान करता है।",
            dept_title: "राज्य कृषि विभाग एवं कृषि भवन",
            dept_desc: "जिला कृषि अधिकारी (DAO) और विकास खंड स्तर के कृषि प्रसार अधिकारी (ADO) जो खेत निरीक्षण और अनुदानित सहायता प्रदान करते हैं।",
            univ_title: "कृषि विश्वविद्यालय (SAUs) एवं ICAR अनुसंधान संस्थान",
            univ_desc: "विशेष पादप रोग क्लिनिक, प्रयोगशाला जांच और उन्नत फसल प्रबंधन मार्गदर्शन प्रदान करने वाले प्रमुख शैक्षणिक संस्थान।",
            location_label: "अपना जिला KVK और कृषि कार्यालय खोजें:",
            location_placeholder: "राज्य, जिला, कस्बा या पिन कोड दर्ज करें (उदा: Karnal, Pune, Patna, 132001)...",
            search_btn: "🔍 स्थानीय KVK / कार्यालय खोजें",
            detect_btn: "🎯 मेरी लोकेशन का उपयोग करें (वैकल्पिक)",
            results_for: "कृषि विस्तार एवं KVK विकल्प:",
            summary_title: "किसान परामर्श सारांश जनरेटर",
            summary_desc: "कृषि वैज्ञानिक या विस्तार अधिकारी से WhatsApp, SMS या सीधे साझा करने के लिए अपनी फसल रोग निदान का व्यवस्थित सारांश तैयार करें।",
            crop_label: "फसल का नाम:",
            disease_label: "दृश्य निदान / संभावित रोग:",
            confidence_label: "दृश्य विश्वसनीयता स्तर:",
            symptoms_label: "देखे गए पत्ती व खेत के लक्षण (आपकी टिप्पणियां):",
            symptoms_placeholder: "उदा: निचली पत्तियों पर संकेंद्री छल्लों वाले गहरे गोल धब्बे, 3 दिन पहले बारिश के बाद दिखे...",
            severity_label: "नुकसान की गंभीरता / फैलाव:",
            severity_opt1: "कम (कुछ पत्तियां / छिटपुट पौधे)",
            severity_opt2: "मध्यम (10% - 25% फसल प्रभावित)",
            severity_opt3: "गंभीर (> 25% खेत प्रभावित / तेजी से प्रसार)",
            generate_btn: "📝 परामर्श सारांश अपडेट करें",
            copy_btn: "📋 विशेषज्ञ हेतु सारांश कॉपी करें",
            copied_text: "✓ परामर्श सारांश क्लिपबोर्ड पर कॉपी हो गया! साझा करने के लिए तैयार।",
            preview_title: "परामर्श सारांश पूर्वावलोकन",
            auto_loaded_note: "✓ इस उपकरण पर आपके सबसे हालिया फसल निदान से स्वतः भरा गया।"
        },
        about: {
            section_label: "कार्यप्रणाली",
            title: "क्रॉपक्योर AI कैसे कार्य करता है",
            stage1_title: "1. तस्वीर अपलोड",
            stage1_desc: "अपने फोन या कंप्यूटर से रोगग्रस्त फसल की पत्ती की स्पष्ट तस्वीर चुनें।",
            stage2_title: "2. CNN रोग निदान",
            stage2_desc: "हमारा प्रशिक्षित CNN मॉडल पत्ती के दृश्य पैटर्न का विश्लेषण कर संभावित रोग श्रेणियों की गणना करता है।",
            stage3_title: "3. ज्ञान पुनर्प्राप्ति (RAG)",
            stage3_desc: "FAISS रिट्रीवर कृषि ज्ञानकोष से सत्यापित लक्षण, उपचार और रोकथाम के उपाय खोजता है।",
            stage4_title: "4. एआई कृषि मार्गदर्शन",
            stage4_desc: "Groq LLM केवल पुनर्प्राप्त कृषि ज्ञान पर आधारित स्पष्ट और व्यावहारिक किसान परामर्श तैयार करता है।"
        },
        crops: {
            Apple: "सेब",
            Corn: "मक्का",
            Potato: "आलू",
            Tomato: "टमाटर",
            Grape: "अंगूर"
        },
        diseases: {
            Apple_Healthy: "सेब (स्वस्थ)",
            Apple_Rust: "सेब का रतुआ (गेरुआ) रोग",
            Apple_Scab: "सेब का स्कैब रोग",
            Corn_Gray_Leaf_Spot: "मक्का का धूसर पर्ण धब्बा रोग",
            Corn_Leaf_Blight: "मक्का का पर्ण अंगमारी (झुलसा) रोग",
            Corn_Leaf_Rust: "मक्का का रतुआ रोग",
            Potato_Early_Blight: "आलू का अगेती झुलसा रोग",
            Potato_Late_Blight: "आलू का पछेती झुलसा रोग",
            Potato_Leaf_Blight: "आलू का पर्ण झुलसा रोग",
            Potato_Leafroll_Virus: "आलू का पत्ती मोड़क (लीफरोल) वायरस",
            Potato_Healthy: "आलू (स्वस्थ)",
            Tomato_Bacterial_Spot: "टमाटर का जीवाणु जनित धब्बा रोग",
            Tomato_Early_Blight: "टमाटर का अगेती झुलसा रोग",
            Tomato_Late_Blight: "टमाटर का पछेती झुलसा रोग",
            Tomato_Leaf_Mold: "टमाटर का पर्ण फफूंदी रोग",
            Tomato_Septoria_Leaf_Spot: "टमाटर का सेप्टोरिया पर्ण धब्बा रोग",
            Tomato_Healthy: "टमाटर (स्वस्थ)",
            Grape_Black_Rot: "अंगूर का ब्लैक रॉट (काला सड़न) रोग"
        }
    }
};

// Language Helpers
function getCurrentLanguage() {
    try {
        const stored = localStorage.getItem("cropcure_lang");
        if (stored && ["en", "te", "hi"].includes(stored)) {
            return stored;
        }
    } catch (e) {
        // localStorage unavailable
    }
    return "en";
}

function setLanguage(lang) {
    if (!["en", "te", "hi"].includes(lang)) {
        lang = "en";
    }
    try {
        localStorage.setItem("cropcure_lang", lang);
    } catch (e) {
        // localStorage unavailable
    }
    applyTranslations(lang);
    window.dispatchEvent(new CustomEvent("cropcureLanguageChanged", { detail: { language: lang } }));
}

function t(path, lang = null) {
    const activeLang = lang || getCurrentLanguage();
    const dict = TRANSLATIONS[activeLang] || TRANSLATIONS.en;
    const parts = path.split(".");
    let current = dict;
    for (const p of parts) {
        if (current && typeof current === "object" && p in current) {
            current = current[p];
        } else {
            // Fallback to English
            let fallback = TRANSLATIONS.en;
            for (const fp of parts) {
                if (fallback && typeof fallback === "object" && fp in fallback) {
                    fallback = fallback[fp];
                } else {
                    return path;
                }
            }
            return fallback;
        }
    }
    return current || path;
}

function translateCrop(cropName, lang = null) {
    if (!cropName) return "";
    const activeLang = lang || getCurrentLanguage();
    const dict = TRANSLATIONS[activeLang]?.crops || TRANSLATIONS.en.crops;
    return dict[cropName] || TRANSLATIONS.en.crops[cropName] || cropName;
}

function translateDisease(diseaseName, lang = null) {
    if (!diseaseName) return "";
    const cleanKey = String(diseaseName).trim().replace(/ /g, "_");
    const activeLang = lang || getCurrentLanguage();
    const dict = TRANSLATIONS[activeLang]?.diseases || TRANSLATIONS.en.diseases;
    if (dict[cleanKey]) return dict[cleanKey];
    if (TRANSLATIONS.en.diseases[cleanKey]) return TRANSLATIONS.en.diseases[cleanKey];

    // Split Crop_Disease if possible
    const parts = cleanKey.split("_");
    if (parts.length >= 2) {
        const crop = parts[0];
        const rest = parts.slice(1).join(" ");
        const transCrop = translateCrop(crop, activeLang);
        return `${transCrop} ${rest}`;
    }
    return String(diseaseName).replace(/_/g, " ");
}

function applyTranslations(lang = null) {
    const activeLang = lang || getCurrentLanguage();
    document.documentElement.lang = activeLang;

    // Update all elements with data-i18n
    const elements = document.querySelectorAll("[data-i18n]");
    elements.forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (key) {
            const translation = t(key, activeLang);
            if (translation) {
                el.textContent = translation;
            }
        }
    });

    // Update placeholders with data-i18n-placeholder
    const inputElements = document.querySelectorAll("[data-i18n-placeholder]");
    inputElements.forEach(el => {
        const key = el.getAttribute("data-i18n-placeholder");
        if (key) {
            const translation = t(key, activeLang);
            if (translation) {
                el.placeholder = translation;
            }
        }
    });

    // Sync all language selectors in DOM
    const selectors = document.querySelectorAll(".language-dropdown");
    selectors.forEach(sel => {
        sel.value = activeLang;
    });
}

// Export for Node/Tests and Browser
if (typeof window !== "undefined") {
    window.TRANSLATIONS = TRANSLATIONS;
    window.getCurrentLanguage = getCurrentLanguage;
    window.setLanguage = setLanguage;
    window.t = t;
    window.translateCrop = translateCrop;
    window.translateDisease = translateDisease;
    window.applyTranslations = applyTranslations;
}

if (typeof global !== "undefined") {
    global.TRANSLATIONS = TRANSLATIONS;
    global.getCurrentLanguage = getCurrentLanguage;
    global.setLanguage = setLanguage;
    global.t = t;
    global.translateCrop = translateCrop;
    global.translateDisease = translateDisease;
    global.applyTranslations = applyTranslations;
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        TRANSLATIONS,
        getCurrentLanguage,
        setLanguage,
        t,
        translateCrop,
        translateDisease,
        applyTranslations
    };
}
