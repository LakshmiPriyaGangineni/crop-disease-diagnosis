// =========================================
// CropCure AI - Frontend JavaScript
// =========================================

// State
let currentPrediction = null;

// DOM Elements - Image Upload
const imageInput = document.getElementById("imageInput");
const uploadButton = document.getElementById("uploadButton");
const previewContainer = document.getElementById("previewContainer");
const imagePreview = document.getElementById("imagePreview");
const analyzeButton = document.getElementById("analyzeButton");

// DOM Elements - Diagnosis Result
const resultSection = document.getElementById("resultSection");
const diseaseCardTitle = document.getElementById("diseaseCardTitle");
const diseaseName = document.getElementById("diseaseName");
const confidenceElement = document.getElementById("confidence");
const diagnosisBadge = document.getElementById("diagnosisBadge");
const confidenceBadge = document.getElementById("confidenceBadge");
const uncertaintyWarningContainer = document.getElementById("uncertaintyWarningContainer");
const warningTitle = document.getElementById("warningTitle");
const warningMessage = document.getElementById("warningMessage");

const top3Container = document.getElementById("top3Container");
const top3Title = document.getElementById("top3Title");
const top3Subtitle = document.getElementById("top3Subtitle");
const top3List = document.getElementById("top3List");

const symptomsElement = document.getElementById("symptoms");
const treatmentElement = document.getElementById("treatment");
const preventionElement = document.getElementById("prevention");
const groundedContent = document.getElementById("groundedContent");

const diagnosisQuestionInput = document.getElementById("diagnosisQuestionInput");
const diagnosisAskButton = document.getElementById("diagnosisAskButton");

// DOM Elements - Chatbot
const chatInput = document.getElementById("chatInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");


// =========================================
// Open File Selector & Drag and Drop
// =========================================

if (uploadButton && imageInput) {
    uploadButton.addEventListener("click", () => {
        imageInput.click();
    });
}

const uploadCardElement = (typeof document !== "undefined" && document.querySelector) ? document.querySelector(".upload-card") : null;
if (uploadCardElement && uploadCardElement.addEventListener) {
    ["dragenter", "dragover"].forEach(eventName => {
        uploadCardElement.addEventListener(eventName, (e) => {
            if (e && e.preventDefault) e.preventDefault();
            if (e && e.stopPropagation) e.stopPropagation();
            if (uploadCardElement.classList && uploadCardElement.classList.add) {
                uploadCardElement.classList.add("drag-over");
            }
        }, false);
    });

    ["dragleave", "dragend"].forEach(eventName => {
        uploadCardElement.addEventListener(eventName, (e) => {
            if (e && e.preventDefault) e.preventDefault();
            if (e && e.stopPropagation) e.stopPropagation();
            if (uploadCardElement.classList && uploadCardElement.classList.remove) {
                uploadCardElement.classList.remove("drag-over");
            }
        }, false);
    });

    uploadCardElement.addEventListener("drop", (e) => {
        if (e && e.preventDefault) e.preventDefault();
        if (e && e.stopPropagation) e.stopPropagation();
        if (uploadCardElement.classList && uploadCardElement.classList.remove) {
            uploadCardElement.classList.remove("drag-over");
        }
        const dt = e ? e.dataTransfer : null;
        if (dt && dt.files && dt.files.length > 0) {
            const file = dt.files[0];
            if (file && file.type && !file.type.startsWith("image/")) {
                alert("Please drop a valid image file (JPG, PNG).");
                return;
            }
            if (imageInput && typeof DataTransfer !== "undefined") {
                try {
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    imageInput.files = dataTransfer.files;
                } catch (err) {}
            }
            if (imagePreview && typeof URL !== "undefined" && URL.createObjectURL) {
                imagePreview.src = URL.createObjectURL(file);
            }
            if (previewContainer && previewContainer.classList) {
                previewContainer.classList.remove("hidden");
                if (typeof previewContainer.scrollIntoView === "function") {
                    previewContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
                }
            }
        }
    }, false);
}


// =========================================
// When an Image Is Selected
// =========================================

if (imageInput) {
    imageInput.addEventListener("change", () => {
        const file = imageInput.files[0];
        if (!file) return;

        if (!file.type.startsWith("image/")) {
            alert("Please select a valid image file.");
            imageInput.value = "";
            return;
        }

        const imageURL = (typeof URL !== "undefined" && URL.createObjectURL) ? URL.createObjectURL(file) : "";
        if (imagePreview && imageURL) imagePreview.src = imageURL;
        if (previewContainer) previewContainer.classList.remove("hidden");
    });
}


// =========================================
// Helper: Clean Disease Name Formatting
// =========================================

function formatDiseaseName(rawName) {
    if (!rawName) return "—";
    return String(rawName).replace(/_/g, " ").trim();
}


// =========================================
// Helper: HTML Escaper (XSS Protection)
// =========================================

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}


// =========================================
// Helper: Clean Markdown to HTML Parser
// =========================================

function renderMarkdown(text) {
    if (!text) return "";

    // 1. Normalize line endings and convert literal <br> tags to standard newlines
    let clean = String(text)
        .replace(/\r\n/g, "\n")
        .replace(/\r/g, "\n")
        .replace(/<\s*br\s*\/?>/gi, "\n");

    // 2. Escape untrusted HTML characters to prevent XSS
    clean = escapeHtml(clean);

    // 3. Parse Markdown Tables (strip separators and build structured HTML table)
    const sepPattern = /^\s*\|?(\s*:?-+:?\s*\|)+\s*(:?-+:?\s*)?\|?\s*$/;
    const lines = clean.split("\n");
    const outputLines = [];
    let i = 0;

    const splitTableRow = (rowStr) => {
        let r = rowStr.trim();
        if (r.startsWith("|")) r = r.slice(1);
        if (r.endsWith("|")) r = r.slice(0, -1);
        return r.split("|").map(cell => cell.trim());
    };

    while (i < lines.length) {
        const line = lines[i];
        const trimmed = line.trim();

        if (trimmed.includes("|") && i + 1 < lines.length && sepPattern.test(lines[i + 1].trim())) {
            const headerCells = splitTableRow(trimmed);
            i += 2; // skip header and separator row

            const dataRows = [];
            while (i < lines.length && lines[i].trim().includes("|") && !sepPattern.test(lines[i].trim())) {
                dataRows.push(splitTableRow(lines[i].trim()));
                i++;
            }

            const theadTh = headerCells.map(h => `<th>${h}</th>`).join("");
            const tbodyTr = dataRows.map(row => {
                const tds = row.map(c => `<td>${c}</td>`).join("");
                return `<tr>${tds}</tr>`;
            }).join("");

            const tableHtml = `
                <div class="table-responsive">
                    <table class="markdown-table">
                        <thead><tr>${theadTh}</tr></thead>
                        <tbody>${tbodyTr}</tbody>
                    </table>
                </div>
            `;
            outputLines.push(tableHtml);
            continue;
        }

        outputLines.push(line);
        i++;
    }

    let processed = outputLines.join("\n");

    // 4. Headings
    processed = processed.replace(/^#### (.*$)/gim, '<h5>$1</h5>');
    processed = processed.replace(/^### (.*$)/gim, '<h5>$1</h5>');
    processed = processed.replace(/^## (.*$)/gim, '<h4>$1</h4>');
    processed = processed.replace(/^# (.*$)/gim, '<h3>$1</h3>');

    // 5. Bold & Italics & Inline Code
    processed = processed.replace(/\*\*\*(.*?)\*\*\*/gim, '<strong><em>$1</em></strong>');
    processed = processed.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    processed = processed.replace(/\*(.*?)\*/gim, '<em>$1</em>');
    processed = processed.replace(/`([^`]+)`/gim, '<code>$1</code>');

    // 6. Horizontal Rules
    processed = processed.replace(/^(?:---|\*\*\*|___)\s*$/gim, '<hr class="report-hr">');

    // 7. Bullet Lists
    processed = processed.replace(/^\s*[-*]\s+(.*)$/gim, '<li>$1</li>');
    processed = processed.replace(/((?:<li>.*?<\/li>\s*)+)/gim, '<ul>$1</ul>');

    // 8. Paragraphs
    const rawBlocks = processed.split(/\n\s*\n/);
    const htmlBlocks = rawBlocks.map(block => {
        const b = block.trim();
        if (!b) return "";
        if (
            b.startsWith("<h") ||
            b.startsWith("<ul") ||
            b.startsWith("<ol") ||
            b.startsWith("<div") ||
            b.startsWith("<table") ||
            b.startsWith("<hr") ||
            b.startsWith("<li")
        ) {
            return b;
        }
        return `<p>${b.replace(/\n/g, '<br>')}</p>`;
    });

    return htmlBlocks.filter(Boolean).join("\n");
}


// =========================================
// Helper: Extract Section Content from LLM Text
// =========================================

function extractSection(text, targetCategory) {
    if (!text) return "";

    const categoryConfig = {
        symptoms: {
            keywords: ["symptom", "sign", "appearance"],
            stopWords: ["treatment", "control", "cure", "prevention", "prevent"]
        },
        treatment: {
            keywords: ["treatment", "control", "cure", "remedy", "fungicide", "management"],
            stopWords: ["symptom", "prevention", "prevent"]
        },
        prevention: {
            keywords: ["prevention", "prevent", "cultural practice", "prophylaxis"],
            stopWords: ["symptom", "treatment", "control", "cure", "diagnostic"]
        }
    };

    const config = categoryConfig[targetCategory];
    if (!config) return "";

    const clean = String(text)
        .replace(/\r\n/g, "\n")
        .replace(/\r/g, "\n")
        .replace(/<\s*br\s*\/?>/gi, "\n");

    const lines = clean.split("\n");
    let capturing = false;
    let captured = [];

    const headerRegex = /^(?:#{1,5}\s+.*|\s*(?:\d+[\.\)]\s*)?\*\*[A-Za-z0-9\s/&,–—\(\)]+:\*\*\s*$|\s*(?:\d+[\.\)]\s*)?\*\*[A-Za-z0-9\s/&,–—\(\)]+\*\*\s*$|\s*(?:[A-Za-z0-9\s/&,–—\(\)]+):\s*$)/;
    const listItemRegex = /^(?:[-*]|\d+[\.\)])\s+/;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();
        if (!trimmed) {
            if (capturing && captured.length > 0 && captured[captured.length - 1] !== "") {
                captured.push("");
            }
            continue;
        }

        const lower = trimmed.toLowerCase();
        const isListItem = listItemRegex.test(trimmed);
        const isHeader = headerRegex.test(trimmed) && !isListItem;

        const matchesKw = config.keywords.some(k => lower.includes(k));

        if (isHeader) {
            if (matchesKw && !(targetCategory === "treatment" && lower.includes("prevent"))) {
                capturing = true;
                const colonIdx = trimmed.indexOf(":");
                if (colonIdx !== -1) {
                    const afterColon = trimmed.slice(colonIdx + 1).replace(/\*\*/g, "").trim();
                    if (afterColon) {
                        captured.push(afterColon);
                    }
                }
                continue;
            } else if (capturing) {
                // Next distinct section begins
                break;
            }
        }

        if (capturing) {
            captured.push(line);
        }
    }

    return captured.join("\n").trim();
}


// =========================================
// Analyze Button Click (CNN Prediction + RAG)
// =========================================

if (analyzeButton) {
    analyzeButton.addEventListener("click", async () => {
        const file = imageInput ? imageInput.files[0] : null;
        if (!file) {
            alert("Please select a crop leaf image first.");
            return;
        }

        analyzeButton.disabled = true;
        analyzeButton.textContent = "Analyzing Image...";

    try {
        const formData = new FormData();
        formData.append("image", file);

        // Step 1: POST /predict
        const response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        console.log("/predict backend response:", result);

        if (!response.ok) {
            throw new Error(result.message || "Prediction failed.");
        }

        // Store current prediction state
        currentPrediction = result;
        try {
            sessionStorage.setItem("cropcure_last_diagnosis", JSON.stringify(result));
        } catch (e) {
            console.warn("Could not save diagnosis to sessionStorage:", e);
        }

        // Step 2: Display CNN prediction and top-3 candidates
        displayPredictionResult(result);

        // Step 3: Automatically fetch grounded RAG + LLM health analysis
        const defaultQuestion = "What are the symptoms, treatment and prevention for this disease?";
        await fetchHealthAnalysis(defaultQuestion, result);

    } catch (error) {
        console.error("Diagnosis error:", error);
        alert(
            "Diagnosis error: " + (error.message || "Unable to connect to CropCure AI backend.")
        );
    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze Disease";
    }
});
}


// =========================================
// Display CNN Prediction & Top-3 Candidates
// =========================================

function displayPredictionResult(result) {
    const disease = result.predicted_class || result.prediction || "Unknown";
    const confValue = Number(result.confidence || 0);
    const isLowConfidence = confValue < 0.50;
    const formattedConf = (confValue * 100).toFixed(2) + "%";

    confidenceElement.textContent = formattedConf;

    // Display explicit uncertainty banner if present
    if (uncertaintyWarningContainer) {
        if (result.warning || isLowConfidence) {
            uncertaintyWarningContainer.className = "uncertainty-warning-container warning-box-uncertain";

            if (warningTitle) {
                warningTitle.textContent = (typeof t === "function" ? t("diagnosis.uncertain_warning_title") : null) || "⚠️ Uncertain Visual Diagnosis (< 50% Confidence)";
            }
            if (warningMessage) {
                const localizedWarning = (typeof t === "function" ? t("diagnosis.uncertain_warning_desc") : null);
                warningMessage.textContent = localizedWarning || result.warning || (
                    `Visual diagnosis is uncertain (${formattedConf} < 50.0%). ` +
                    "The model could not distinguish a single class with high certainty. " +
                    "Review top candidate alternatives before taking action."
                );
            }
            uncertaintyWarningContainer.classList.remove("hidden");
        } else {
            uncertaintyWarningContainer.classList.add("hidden");
        }
    }

    const localizedDisease = (typeof translateDisease === "function") ? translateDisease(disease) : formatDiseaseName(disease);

    if (isLowConfidence) {
        // Guardrail: Do NOT present prediction as certain
        if (diseaseCardTitle) {
            diseaseCardTitle.textContent = (typeof t === "function" ? t("diagnosis.uncertain_title") : null) || "Visual Diagnosis (Uncertain)";
        }
        const uncertainStatusText = (typeof t === "function" ? t("diagnosis.uncertain_title") : null) || "⚠️ Uncertain visual diagnosis";
        const topCandidatePrefix = (typeof getCurrentLanguage === "function" && getCurrentLanguage() === "te")
            ? "ప్రధాన అభ్యర్థి:"
            : ((typeof getCurrentLanguage === "function" && getCurrentLanguage() === "hi") ? "शीर्ष संभावित विकल्प:" : "Top candidate:");

        diseaseName.innerHTML = `
            <span class="uncertain-title">${escapeHtml(uncertainStatusText)}</span>
            <span class="uncertain-sub">${escapeHtml(topCandidatePrefix)} ${escapeHtml(localizedDisease)}</span>
        `;

        if (diagnosisBadge) {
            diagnosisBadge.className = "diagnosis-badge badge-uncertain";
            diagnosisBadge.textContent = (typeof t === "function" ? t("diagnosis.uncertain_badge") : null) || "Uncertain Diagnosis (< 50%)";
            diagnosisBadge.classList.remove("hidden");
        }
        if (confidenceBadge) {
            confidenceBadge.className = "confidence-badge badge-uncertain";
            confidenceBadge.textContent = (typeof t === "function" ? t("diagnosis.low_conf_badge") : null) || "Low Confidence";
            confidenceBadge.classList.remove("hidden");
        }
    } else {
        // High confidence: Primary visual diagnosis
        if (diseaseCardTitle) {
            diseaseCardTitle.textContent = (typeof t === "function" ? t("diagnosis.primary_title") : null) || "Primary Visual Diagnosis";
        }
        diseaseName.textContent = localizedDisease;

        if (diagnosisBadge) {
            diagnosisBadge.className = "diagnosis-badge badge-confident";
            diagnosisBadge.textContent = (typeof t === "function" ? t("diagnosis.primary_title") : null) || "Primary Visual Diagnosis (≥ 50%)";
            diagnosisBadge.classList.remove("hidden");
        }
        if (confidenceBadge) {
            confidenceBadge.className = "confidence-badge badge-confident";
            confidenceBadge.textContent = (typeof t === "function" ? t("diagnosis.high_conf_badge") : null) || "High Confidence";
            confidenceBadge.classList.remove("hidden");
        }
    }

    // Render Top-3 Candidates
    if (result.top3 && Array.isArray(result.top3) && result.top3.length > 0) {
        renderTop3List(result.top3, isLowConfidence);
        top3Container.classList.remove("hidden");
    } else {
        top3Container.classList.add("hidden");
    }

    // Set loading placeholders for Health Analysis area
    symptomsElement.innerHTML = `<em>Retrieving symptoms from RAG knowledge base...</em>`;
    treatmentElement.innerHTML = `<em>Retrieving treatment recommendations...</em>`;
    preventionElement.innerHTML = `<em>Retrieving prevention measures...</em>`;

    groundedContent.innerHTML = `
        <div class="loading-spinner-container">
            <div class="spinner"></div>
            <p>Querying agricultural knowledge base and generating grounded advice via Groq LLM...</p>
        </div>
    `;

    // Reveal result section and scroll into view
    resultSection.classList.remove("hidden");
    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// =========================================
// Render Top-3 Candidates List
// =========================================

function renderTop3List(top3, isLowConfidence) {
    if (isLowConfidence) {
        top3Title.textContent = (typeof t === "function" ? t("diagnosis.top3_title") : null) || "⚠️ Uncertain Diagnosis — Top 3 Candidates";
        top3Subtitle.textContent = (typeof t === "function" ? t("diagnosis.top3_subtitle") : null) || "The image confidence is under 50%. The deep learning model identified these alternative possibilities:";
    } else {
        top3Title.textContent = (typeof t === "function" ? t("diagnosis.top3_title") : null) || "Top 3 Visual Matches";
        top3Subtitle.textContent = (typeof t === "function" ? t("diagnosis.top3_subtitle") : null) || "Confidence breakdown across the highest-ranked disease classes:";
    }

    top3List.innerHTML = top3.map((item, index) => {
        const name = (typeof translateDisease === "function") ? translateDisease(item.class) : formatDiseaseName(item.class);
        const prob = Number(item.probability || 0);
        const pct = (prob * 100).toFixed(1);
        const barClass = isLowConfidence ? "top3-progress-fill fill-uncertain" : "top3-progress-fill";

        return `
            <div class="top3-item">
                <div class="top3-info">
                    <span class="top3-name">
                        <span class="top3-rank">${index + 1}</span>
                        ${escapeHtml(name)}
                    </span>
                    <span class="top3-prob">${pct}%</span>
                </div>
                <div class="top3-progress-bg">
                    <div class="${barClass}" style="width: ${pct}%;"></div>
                </div>
            </div>
        `;
    }).join("");
}


// =========================================
// Fetch Grounded RAG + LLM Health Analysis
// =========================================

async function fetchHealthAnalysis(question, prediction) {
    try {
        const currentLang = typeof getCurrentLanguage === "function" ? getCurrentLanguage() : "en";
        const payload = {
            message: question,
            predicted_disease: prediction.predicted_class || prediction.prediction,
            confidence: prediction.confidence,
            top3: prediction.top3,
            language: currentLang
        };

        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const chatResult = await response.json();
        console.log("/chat backend response:", chatResult);

        if (!response.ok) {
            throw new Error(chatResult.message || "Chat request failed.");
        }

        const answerText = chatResult.answer || chatResult.response || "No response received.";
        const isLowConfidence = Number(prediction.confidence || 0) < 0.50;

        // Render full grounded response in the Health Advisory area
        groundedContent.innerHTML = renderMarkdown(answerText);

        // Intelligently populate Symptoms, Treatment, Prevention cards
        populateInformationCards(answerText, isLowConfidence, prediction, chatResult);

        // Also add consultation message to chatbot history
        const diseaseLabel = (typeof translateDisease === "function")
            ? translateDisease(prediction.predicted_class)
            : formatDiseaseName(prediction.predicted_class);
        addChatMessage(
            `Diagnosis consultation for **${diseaseLabel}**:\n\n${answerText}`,
            "ai"
        );

    } catch (error) {
        console.error("Health analysis error:", error);
        groundedContent.innerHTML = `
            <p style="color: #b91c1c;">
                <strong>Notice:</strong> Unable to complete agricultural guidance retrieval: ${escapeHtml(error.message)}.
                Please ensure the Flask backend and Groq LLM are active.
            </p>
        `;
        if (prediction && prediction.knowledge) {
            populateInformationCards("", isLowConfidence, prediction, null);
        } else {
            symptomsElement.innerHTML = `<p class="info-missing">Symptom information is not available in the current knowledge base.</p>`;
            treatmentElement.innerHTML = `<p class="info-missing">Treatment information is not available in the current knowledge base.</p>`;
            preventionElement.innerHTML = `<p class="info-missing">Prevention information is not available in the current knowledge base.</p>`;
        }
    }
}


// =========================================
// Populate Symptoms, Treatment, Prevention Cards
// =========================================

function populateInformationCards(answerText, isLowConfidence, prediction, chatResult) {
    const symptomsText = extractSection(answerText, "symptoms");
    const treatmentText = extractSection(answerText, "treatment");
    const preventionText = extractSection(answerText, "prevention");

    const primaryKnowledge = (chatResult && chatResult.knowledge) || (prediction && prediction.knowledge) || null;
    const candidates = (chatResult && chatResult.candidates) || [];

    // ==========================================
    // 1. SYMPTOMS CARD
    // ==========================================
    if (isLowConfidence) {
        let symHtml = `
            <div class="card-lead-note">
                <strong>Differential Symptoms:</strong> Visual features overlap among candidate diseases. Compare symptoms across candidates:
            </div>
        `;
        let candidateSymptomsAdded = false;
        if (candidates.length > 0) {
            const items = candidates.filter(c => c.has_knowledge && c.symptoms && c.symptoms.length > 0);
            if (items.length > 0) {
                symHtml += `<div class="candidate-info-block">`;
                items.forEach(c => {
                    const symList = Array.isArray(c.symptoms) ? c.symptoms.join("; ") : c.symptoms;
                    symHtml += `
                        <div class="candidate-info-row">
                            <strong>${escapeHtml(c.clean_name || c.disease)}:</strong> ${escapeHtml(symList)}
                        </div>
                    `;
                });
                symHtml += `</div>`;
                candidateSymptomsAdded = true;
            }
        }
        if (!candidateSymptomsAdded && symptomsText) {
            symHtml += renderMarkdown(symptomsText);
        } else if (!candidateSymptomsAdded) {
            symHtml += `<p class="info-missing">Symptom information is not available in the current knowledge base.</p>`;
        }
        symptomsElement.innerHTML = symHtml;
    } else {
        if (symptomsText) {
            symptomsElement.innerHTML = renderMarkdown(symptomsText);
        } else if (primaryKnowledge && primaryKnowledge.symptoms && primaryKnowledge.symptoms.length > 0) {
            const sym = Array.isArray(primaryKnowledge.symptoms)
                ? primaryKnowledge.symptoms.map(s => `<li>${escapeHtml(s)}</li>`).join("")
                : `<li>${escapeHtml(primaryKnowledge.symptoms)}</li>`;
            symptomsElement.innerHTML = `<ul>${sym}</ul>`;
        } else {
            symptomsElement.innerHTML = `<p class="info-missing">Symptom information is not available in the current knowledge base.</p>`;
        }
    }

    // ==========================================
    // 2. TREATMENT CARD (Safety Guardrails)
    // ==========================================
    if (isLowConfidence) {
        treatmentElement.innerHTML = `
            <div class="provisional-notice">
                <p><strong>⚠️ Provisional Guidance Only:</strong> Visual diagnosis confidence is below 50%. Specific chemical or crop-specific treatments are <strong>not confirmed</strong> and should not be applied yet.</p>
                <p>Verify physical leaf symptoms and compare candidate possibilities in the detailed AI Agricultural Guidance below before applying any disease-specific treatment.</p>
            </div>
        `;
    } else {
        if (treatmentText) {
            treatmentElement.innerHTML = renderMarkdown(treatmentText);
        } else if (primaryKnowledge && primaryKnowledge.treatment && primaryKnowledge.treatment.trim()) {
            treatmentElement.innerHTML = renderMarkdown(primaryKnowledge.treatment);
        } else {
            treatmentElement.innerHTML = `<p class="info-missing">Treatment information is not available in the current knowledge base.</p>`;
        }
    }

    // ==========================================
    // 3. PREVENTION CARD
    // ==========================================
    if (isLowConfidence) {
        let prevHtml = `
            <div class="card-lead-note">
                <strong>Candidate Prevention Protocols:</strong> Supported prevention measures retrieved from the agricultural knowledge base:
            </div>
        `;
        let candidatePrevFound = false;
        if (candidates.length > 0) {
            const withPrev = candidates.filter(c => c.has_knowledge && c.prevention && c.prevention.trim());
            if (withPrev.length > 0) {
                prevHtml += `<div class="candidate-info-block">`;
                withPrev.forEach(c => {
                    prevHtml += `
                        <div class="candidate-info-row">
                            <strong>${escapeHtml(c.clean_name || c.disease)}:</strong> ${escapeHtml(c.prevention)}
                        </div>
                    `;
                });
                prevHtml += `</div>`;
                candidatePrevFound = true;
            }
        }
        if (!candidatePrevFound && preventionText) {
            prevHtml += renderMarkdown(preventionText);
            candidatePrevFound = true;
        }

        if (candidatePrevFound) {
            preventionElement.innerHTML = prevHtml;
        } else {
            preventionElement.innerHTML = `<p class="info-missing">Prevention information is not available in the current knowledge base.</p>`;
        }
    } else {
        // High confidence: Display prevention advice only when supported by retrieved agricultural knowledge
        if (preventionText) {
            preventionElement.innerHTML = renderMarkdown(preventionText);
        } else if (primaryKnowledge && primaryKnowledge.prevention && primaryKnowledge.prevention.trim()) {
            preventionElement.innerHTML = renderMarkdown(primaryKnowledge.prevention);
        } else {
            preventionElement.innerHTML = `<p class="info-missing">Prevention information is not available in the current knowledge base.</p>`;
        }
    }
}


// =========================================
// Interactive Follow-up Question in Diagnosis
// =========================================

if (diagnosisAskButton && diagnosisQuestionInput) {
    const handleDiagnosisQuestion = async () => {
        const question = diagnosisQuestionInput.value.trim();
        if (!question) return;

        if (!currentPrediction) {
            alert("Please analyze a crop leaf image first.");
            return;
        }

        diagnosisAskButton.disabled = true;
        diagnosisAskButton.textContent = "Asking...";

        groundedContent.innerHTML = `
            <div class="loading-spinner-container">
                <div class="spinner"></div>
                <p>Generating answer for: "${question}"...</p>
            </div>
        `;

        await fetchHealthAnalysis(question, currentPrediction);

        diagnosisQuestionInput.value = "";
        diagnosisAskButton.disabled = false;
        diagnosisAskButton.textContent = "Ask CropCure";
    };

    diagnosisAskButton.addEventListener("click", handleDiagnosisQuestion);

    diagnosisQuestionInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            handleDiagnosisQuestion();
        }
    });
}


// =========================================
// AI Assistant Chatbot
// =========================================

if (sendButton) {
    sendButton.addEventListener("click", sendChatMessage);
}

if (chatInput) {
    chatInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            sendChatMessage();
        }
    });
}

async function sendChatMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addChatMessage(message, "user");
    chatInput.value = "";

    try {
        const currentLang = typeof getCurrentLanguage === "function" ? getCurrentLanguage() : "en";
        const payload = {
            message: message,
            language: currentLang
        };

        // Contextualize with current diagnosed image if present
        if (currentPrediction) {
            payload.predicted_disease = currentPrediction.predicted_class;
            payload.confidence = currentPrediction.confidence;
            payload.top3 = currentPrediction.top3;
        }

        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        console.log("Chat backend response:", result);

        if (!response.ok) {
            throw new Error(result.message || "Chat request failed.");
        }

        // Backend returns "answer" field
        const answer = result.answer || result.response || "No response received from the AI assistant.";
        addChatMessage(answer, "ai");

    } catch (error) {
        console.error("Chat error:", error);
        addChatMessage(
            "Unable to connect to the AI assistant. Please make sure the Flask backend is running.",
            "ai"
        );
    }
}


// =========================================
// Add Chat Message to UI
// =========================================

function addChatMessage(message, sender) {
    const messageWrapper = document.createElement("div");
    messageWrapper.classList.add("chat-message");
    if (sender === "user") {
        messageWrapper.classList.add("user-message");
    } else {
        messageWrapper.classList.add("ai-message");
    }

    const avatar = document.createElement("div");
    avatar.classList.add("message-avatar");

    const content = document.createElement("div");
    content.classList.add("message-content");

    const name = document.createElement("strong");

    if (sender === "user") {
        avatar.textContent = "👤";
        name.textContent = "You";
        const text = document.createElement("p");
        text.textContent = message;
        content.appendChild(name);
        content.appendChild(text);
    } else {
        avatar.textContent = "🌱";
        name.textContent = "CropCure AI";
        const renderedDiv = document.createElement("div");
        renderedDiv.innerHTML = renderMarkdown(message);
        content.appendChild(name);
        content.appendChild(renderedDiv);
    }

    messageWrapper.appendChild(avatar);
    messageWrapper.appendChild(content);
    chatMessages.appendChild(messageWrapper);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


// =========================================
// Model Performance & Evaluation Metrics (Step 3)
// =========================================

let evaluationMetricsData = null;

// DOM Elements - Performance Section
const performanceLoading = document.getElementById("performanceLoading");
const performanceError = document.getElementById("performanceError");
const performanceErrorMessage = document.getElementById("performanceErrorMessage");
const performanceContent = document.getElementById("performanceContent");
const retryEvaluationBtn = document.getElementById("retryEvaluationBtn");

const overallAccuracyVal = document.getElementById("overallAccuracyVal");
const overallAccuracyCount = document.getElementById("overallAccuracyCount");
const top3AccuracyVal = document.getElementById("top3AccuracyVal");
const macroPrecisionVal = document.getElementById("macroPrecisionVal");
const macroRecallVal = document.getElementById("macroRecallVal");
const macroF1Val = document.getElementById("macroF1Val");

const comparisonTableBody = document.getElementById("comparisonTableBody");
const splitDetailsGrid = document.getElementById("splitDetailsGrid");
const perClassTableBody = document.getElementById("perClassTableBody");
const classFilterInput = document.getElementById("classFilterInput");

const confusionMatrixTable = document.getElementById("confusionMatrixTable");
const toggleMatrixViewBtn = document.getElementById("toggleMatrixViewBtn");
const interactiveMatrixContainer = document.getElementById("interactiveMatrixContainer");
const staticMatrixContainer = document.getElementById("staticMatrixContainer");
const evaluationDisclaimer = document.getElementById("evaluationDisclaimer");

// Helper: Extract Crop from Class Name
function extractCrop(className) {
    if (!className) return "—";
    const parts = String(className).split("_");
    return parts[0] || "Unknown";
}

// Fetch and Render Evaluation Metrics
async function fetchEvaluationMetrics() {
    if (!performanceLoading) return;

    performanceLoading.classList.remove("hidden");
    if (performanceError) performanceError.classList.add("hidden");
    if (performanceContent) performanceContent.classList.add("hidden");

    try {
        const response = await fetch("http://127.0.0.1:5000/evaluation");
        const data = await response.json();

        if (!response.ok || data.status !== "success") {
            throw new Error(data.message || `HTTP ${response.status}: Failed to fetch evaluation metrics.`);
        }

        evaluationMetricsData = data;

        // Render sections
        renderOverviewMetrics(data);
        renderComparisonTable(data);
        renderSplitDetails(data.split_details);
        renderPerClassTable(data.per_class_metrics);
        renderConfusionMatrix(data.confusion_matrix);

        if (evaluationDisclaimer && data.disclaimer) {
            evaluationDisclaimer.textContent = data.disclaimer;
        }

        performanceLoading.classList.add("hidden");
        if (performanceContent) performanceContent.classList.remove("hidden");

    } catch (err) {
        console.error("Evaluation loading error:", err);
        if (performanceLoading) performanceLoading.classList.add("hidden");
        if (performanceError) {
            if (performanceErrorMessage) {
                performanceErrorMessage.textContent = err.message || "Could not retrieve metrics from backend.";
            }
            performanceError.classList.remove("hidden");
        }
    }
}

// Render Overview Metrics
function renderOverviewMetrics(data) {
    const summary = data.summary || {};
    const macro = data.macro_metrics || {};

    if (overallAccuracyVal) {
        overallAccuracyVal.textContent = summary.overall_test_accuracy_pct !== undefined
            ? `${summary.overall_test_accuracy_pct}%`
            : `${(Number(summary.overall_test_accuracy || 0) * 100).toFixed(2)}%`;
    }
    if (overallAccuracyCount) {
        overallAccuracyCount.textContent = `${summary.total_correct || 0} / ${summary.total_test_images || 0} test images correct`;
    }
    if (top3AccuracyVal) {
        top3AccuracyVal.textContent = summary.top3_accuracy_pct !== undefined
            ? `${summary.top3_accuracy_pct}%`
            : `${(Number(summary.top3_accuracy || 0) * 100).toFixed(2)}%`;
    }
    if (macroPrecisionVal) {
        macroPrecisionVal.textContent = `${(Number(macro.precision || 0) * 100).toFixed(2)}%`;
    }
    if (macroRecallVal) {
        macroRecallVal.textContent = `${(Number(macro.recall || 0) * 100).toFixed(2)}%`;
    }
    if (macroF1Val) {
        macroF1Val.textContent = `${(Number(macro.f1_score || 0) * 100).toFixed(2)}%`;
    }
}

// Render Macro vs Weighted Comparison Table
function renderComparisonTable(data) {
    if (!comparisonTableBody) return;
    const macro = data.macro_metrics || {};
    const weighted = data.weighted_metrics || {};

    comparisonTableBody.innerHTML = `
        <tr>
            <td>
                <span class="badge-pill-macro">Macro Average</span>
                <div style="font-size:0.8rem; color:#6b7280; margin-top:2px;">Equal weight per class</div>
            </td>
            <td><strong>${(Number(macro.precision || 0) * 100).toFixed(2)}%</strong></td>
            <td><strong>${(Number(macro.recall || 0) * 100).toFixed(2)}%</strong></td>
            <td><strong>${(Number(macro.f1_score || 0) * 100).toFixed(2)}%</strong></td>
            <td>Unweighted arithmetic mean across all 17 classes (sensitive to low-sample web classes)</td>
        </tr>
        <tr>
            <td>
                <span class="badge-pill-weighted">Weighted Average</span>
                <div style="font-size:0.8rem; color:#6b7280; margin-top:2px;">Support-weighted</div>
            </td>
            <td><strong>${(Number(weighted.precision || 0) * 100).toFixed(2)}%</strong></td>
            <td><strong>${(Number(weighted.recall || 0) * 100).toFixed(2)}%</strong></td>
            <td><strong>${(Number(weighted.f1_score || 0) * 100).toFixed(2)}%</strong></td>
            <td>Weighted by test sample support per class (reflects volume on prevalent farm classes)</td>
        </tr>
    `;
}

// Render Dataset Split Details
function renderSplitDetails(split) {
    if (!splitDetailsGrid) return;
    split = split || {};

    const items = [
        { label: "Evaluation Split", val: split.evaluation_split || "data/unified_test" },
        { label: "Split Strategy", val: split.split_description || "70% Train / 15% Val / 15% Test" },
        { label: "Test Sample Count", val: `${split.total_test_images || 1903} images` },
        { label: "Total Dataset Volume", val: `${split.total_dataset_images || 12702} images` },
        { label: "Disease Classes", val: `${split.num_classes || 17} classes` },
        { label: "Datasets Unified", val: "PlantVillage + Crops Disease + Web-Sourced" }
    ];

    splitDetailsGrid.innerHTML = items.map(it => `
        <div class="split-detail-item">
            <div class="detail-label">${escapeHtml(it.label)}</div>
            <div class="detail-val">${escapeHtml(it.val)}</div>
        </div>
    `).join("");
}

// Render Per-Class Performance Table
function renderPerClassTable(perClass) {
    if (!perClassTableBody || !perClass) return;

    const classEntries = Object.entries(perClass);
    // Sort by class_index
    classEntries.sort((a, b) => (a[1].class_index || 0) - (b[1].class_index || 0));

    perClassTableBody.innerHTML = classEntries.map(([clsName, metrics]) => {
        const crop = extractCrop(clsName);
        const cleanName = formatDiseaseName(clsName);
        const prec = (Number(metrics.precision || 0) * 100).toFixed(1) + "%";
        const rec = (Number(metrics.recall || 0) * 100).toFixed(1) + "%";
        const f1 = (Number(metrics.f1_score || 0) * 100).toFixed(1) + "%";
        const acc = (Number(metrics.accuracy || 0) * 100).toFixed(1) + "%";

        return `
            <tr data-class="${escapeHtml(clsName.toLowerCase())}" data-crop="${escapeHtml(crop.toLowerCase())}">
                <td style="color:#6b7280; font-size:0.8rem;">${metrics.class_index !== undefined ? metrics.class_index + 1 : "—"}</td>
                <td class="class-name-cell">${cleanName}</td>
                <td><span class="crop-pill">${crop}</span></td>
                <td class="num-cell"><strong>${metrics.test_images || 0}</strong></td>
                <td class="num-cell" style="color:#166534;">${metrics.correct || 0}</td>
                <td class="num-cell" style="color:#b91c1c;">${metrics.incorrect || 0}</td>
                <td class="num-cell">${prec}</td>
                <td class="num-cell">${rec}</td>
                <td class="num-cell"><strong>${f1}</strong></td>
                <td class="num-cell">${acc}</td>
            </tr>
        `;
    }).join("");
}

// Render Confusion Matrix
function renderConfusionMatrix(cmData) {
    if (!confusionMatrixTable || !cmData) return;
    const classes = cmData.classes || [];
    const matrix = cmData.matrix || [];

    if (!Array.isArray(matrix) || matrix.length === 0) {
        confusionMatrixTable.innerHTML = `<tr><td>Confusion matrix data is unavailable.</td></tr>`;
        return;
    }

    // Header row
    let theadHtml = `
        <thead>
            <tr>
                <th class="cm-corner" title="Rows = Ground Truth Label, Columns = Predicted Label">True \\ Pred</th>
                ${classes.map((c, idx) => `<th class="cm-header-col" title="${escapeHtml(c)} (Predicted)">C${idx + 1}</th>`).join("")}
            </tr>
        </thead>
    `;

    // Data rows
    let tbodyHtml = "<tbody>";
    for (let i = 0; i < classes.length; i++) {
        const trueClass = classes[i];
        const row = matrix[i] || [];
        tbodyHtml += `<tr>`;
        tbodyHtml += `<th class="cm-header-row" title="${escapeHtml(trueClass)} (True)">C${i + 1}: ${formatDiseaseName(trueClass)}</th>`;

        for (let j = 0; j < classes.length; j++) {
            const predClass = classes[j];
            const val = row[j] !== undefined ? row[j] : 0;
            let cellClass = "cell-zero";
            if (i === j && val > 0) {
                cellClass = "cell-diagonal";
            } else if (val > 0) {
                cellClass = "cell-error";
            }

            const title = `True: ${formatDiseaseName(trueClass)} &#10;Predicted: ${formatDiseaseName(predClass)} &#10;Count: ${val}`;
            tbodyHtml += `<td class="${cellClass}" title="${title}">${val}</td>`;
        }
        tbodyHtml += `</tr>`;
    }
    tbodyHtml += "</tbody>";

    confusionMatrixTable.innerHTML = theadHtml + tbodyHtml;
}

// Event Listeners for Performance Section
if (retryEvaluationBtn) {
    retryEvaluationBtn.addEventListener("click", fetchEvaluationMetrics);
}

if (classFilterInput && perClassTableBody) {
    classFilterInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        const rows = perClassTableBody.querySelectorAll("tr");
        rows.forEach(row => {
            const cName = row.getAttribute("data-class") || "";
            const crop = row.getAttribute("data-crop") || "";
            if (!query || cName.includes(query) || crop.includes(query)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    });
}

if (toggleMatrixViewBtn && interactiveMatrixContainer && staticMatrixContainer) {
    toggleMatrixViewBtn.addEventListener("click", () => {
        const isStaticHidden = staticMatrixContainer.classList.contains("hidden");
        if (isStaticHidden) {
            staticMatrixContainer.classList.remove("hidden");
            interactiveMatrixContainer.classList.add("hidden");
            toggleMatrixViewBtn.textContent = "📊 View Interactive Matrix";
        } else {
            staticMatrixContainer.classList.add("hidden");
            interactiveMatrixContainer.classList.remove("hidden");
            toggleMatrixViewBtn.textContent = "🖼️ View High-Res Chart";
        }
    });
}

// =========================================
// Government Agricultural Schemes (Step 4)
// =========================================

const schemesGridContainer = document.getElementById("schemesGridContainer");
const schemeSearchInput = document.getElementById("schemeSearchInput");
const clearSearchBtn = document.getElementById("clearSearchBtn");
const categoryChipsContainer = document.getElementById("categoryChipsContainer");
const schemesCountVal = document.getElementById("schemesCountVal");

let allGovernmentSchemes = [];
let currentCategoryFilter = "all";
let currentSearchTerm = "";

// Category CSS class helper
function getCategoryBadgeClass(cat) {
    switch (cat) {
        case "financial_assistance": return "cat-financial";
        case "crop_insurance": return "cat-insurance";
        case "irrigation": return "cat-irrigation";
        case "farming_support": return "cat-farming";
        case "organic_soil": return "cat-organic";
        default: return "cat-financial";
    }
}

// Fetch Schemes from Backend
async function fetchGovernmentSchemes() {
    if (!schemesGridContainer) return;

    try {
        const response = await fetch("http://127.0.0.1:5000/schemes");
        const data = await response.json();

        if (!response.ok || data.status !== "success") {
            throw new Error(data.message || `HTTP ${response.status}: Failed to fetch government schemes.`);
        }

        allGovernmentSchemes = data.schemes || [];
        renderGovernmentSchemes();

    } catch (err) {
        console.error("Schemes loading error:", err);
        if (schemesGridContainer) {
            schemesGridContainer.innerHTML = `
                <div class="schemes-empty-state" style="grid-column: 1 / -1;">
                    <div class="empty-icon">⚠️</div>
                    <h3>Unable to Load Government Schemes</h3>
                    <p>${escapeHtml(err.message || "Could not connect to CropCure AI backend service.")}</p>
                    <button class="primary-button" id="retrySchemesBtn" style="margin-top: 10px; padding: 8px 18px; font-size: 0.9rem;">
                        🔄 Retry Loading
                    </button>
                </div>
            `;
            const retryBtn = document.getElementById("retrySchemesBtn");
            if (retryBtn) {
                retryBtn.addEventListener("click", fetchGovernmentSchemes);
            }
        }
    }
}

// Render Schemes with Search and Filter
function renderGovernmentSchemes() {
    if (!schemesGridContainer) return;

    let filtered = allGovernmentSchemes;

    // Filter by Category
    if (currentCategoryFilter && currentCategoryFilter !== "all") {
        filtered = filtered.filter(s => (s.category || "").toLowerCase() === currentCategoryFilter.toLowerCase());
    }

    // Filter by Search Query
    if (currentSearchTerm) {
        const q = currentSearchTerm.toLowerCase();
        filtered = filtered.filter(s => {
            const name = (s.name || "").toLowerCase();
            const hindi = (s.hindi_name || "").toLowerCase();
            const purpose = (s.purpose || "").toLowerCase();
            const benefits = (s.benefits || "").toLowerCase();
            const elig = (s.eligibility || "").toLowerCase();
            const tags = (s.tags || []).join(" ").toLowerCase();
            return name.includes(q) || hindi.includes(q) || purpose.includes(q) || benefits.includes(q) || elig.includes(q) || tags.includes(q);
        });
    }

    // Update count display
    if (schemesCountVal) {
        schemesCountVal.textContent = filtered.length;
    }

    // Handle Empty Results
    if (filtered.length === 0) {
        schemesGridContainer.innerHTML = `
            <div class="schemes-empty-state" style="grid-column: 1 / -1;">
                <div class="empty-icon">🌾</div>
                <h3>No Schemes Found</h3>
                <p>No agricultural schemes matched your current search keyword or category filter.</p>
                <button class="clear-search-btn" id="resetFiltersBtn" style="margin-top: 8px;">
                    Reset All Filters
                </button>
            </div>
        `;
        const resetBtn = document.getElementById("resetFiltersBtn");
        if (resetBtn) {
            resetBtn.addEventListener("click", () => {
                currentCategoryFilter = "all";
                currentSearchTerm = "";
                if (schemeSearchInput) schemeSearchInput.value = "";
                if (clearSearchBtn) clearSearchBtn.style.display = "none";
                if (categoryChipsContainer) {
                    categoryChipsContainer.querySelectorAll(".category-chip").forEach(c => {
                        if (c.getAttribute("data-category") === "all") c.classList.add("active");
                        else c.classList.remove("active");
                    });
                }
                renderGovernmentSchemes();
            });
        }
        return;
    }

    // Render Cards
    const benefitsHeading = (typeof t === "function" ? t("schemes.benefits_heading") : null) || "Key Benefits & Assistance";
    const eligibilityHeading = (typeof t === "function" ? t("schemes.eligibility_heading") : null) || "Eligibility Summary";
    const stepsHeading = (typeof t === "function" ? t("schemes.steps_heading") : null) || "How to Apply (Verified Steps)";

    const cardsHtml = filtered.map(scheme => {
        const catBadgeClass = getCategoryBadgeClass(scheme.category);
        const stepsHtml = (scheme.application_steps || []).map(step => `<li>${escapeHtml(step)}</li>`).join("");

        return `
            <article class="scheme-card" data-category="${escapeHtml(scheme.category)}">
                <div>
                    <div class="scheme-card-header">
                        <div class="scheme-badges">
                            <span class="scheme-cat-badge ${catBadgeClass}">
                                ${escapeHtml(scheme.category_label || scheme.category)}
                            </span>
                            <span class="scheme-verified-badge">
                                ✓ ${escapeHtml(scheme.verification_status || "Verified Central Scheme")}
                            </span>
                        </div>
                        <h3 class="scheme-title">${escapeHtml(scheme.name)}</h3>
                        ${scheme.hindi_name ? `<p class="scheme-hindi-title">${escapeHtml(scheme.hindi_name)}</p>` : ""}
                    </div>

                    <p class="scheme-purpose">${escapeHtml(scheme.purpose)}</p>

                    <div class="scheme-section">
                        <div class="scheme-section-heading">
                            <span>💰</span> ${escapeHtml(benefitsHeading)}
                        </div>
                        <div class="benefit-highlight-box">
                            ${escapeHtml(scheme.benefits)}
                        </div>
                    </div>

                    <div class="scheme-section">
                        <div class="scheme-section-heading">
                            <span>📋</span> ${escapeHtml(eligibilityHeading)}
                        </div>
                        <div class="eligibility-text">
                            ${escapeHtml(scheme.eligibility)}
                        </div>
                    </div>

                    <div class="scheme-section">
                        <div class="scheme-section-heading">
                            <span>📝</span> ${escapeHtml(stepsHeading)}
                        </div>
                        <ol class="steps-list">
                            ${stepsHtml}
                        </ol>
                    </div>
                </div>

                <div class="scheme-card-footer">
                    <span class="last-verified-label">
                        Verified: ${escapeHtml(scheme.last_verified || "October 2026")} · Source: ${escapeHtml(scheme.official_portal || "Official Portal")}
                    </span>
                    <a
                        href="${escapeHtml(scheme.official_link)}"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="btn-portal-link"
                    >
                        Visit Official Portal ↗
                    </a>
                </div>
            </article>
        `;
    }).join("");

    schemesGridContainer.innerHTML = cardsHtml;
}

// Event Listeners for Schemes
if (categoryChipsContainer) {
    categoryChipsContainer.addEventListener("click", (e) => {
        const chip = e.target.closest(".category-chip");
        if (!chip) return;

        categoryChipsContainer.querySelectorAll(".category-chip").forEach(c => c.classList.remove("active"));
        chip.classList.add("active");

        currentCategoryFilter = chip.getAttribute("data-category") || "all";
        renderGovernmentSchemes();
    });
}

if (schemeSearchInput) {
    schemeSearchInput.addEventListener("input", (e) => {
        currentSearchTerm = e.target.value.trim();
        if (clearSearchBtn) {
            clearSearchBtn.style.display = currentSearchTerm ? "inline-block" : "none";
        }
        renderGovernmentSchemes();
    });
}

if (clearSearchBtn) {
    clearSearchBtn.addEventListener("click", () => {
        if (schemeSearchInput) schemeSearchInput.value = "";
        currentSearchTerm = "";
        clearSearchBtn.style.display = "none";
        renderGovernmentSchemes();
    });
}


// =========================================
// Nearby Agricultural Input Shops (Step 5)
// =========================================

const shopLocationInput = document.getElementById("shopLocationInput");
const clearLocationBtn = document.getElementById("clearLocationBtn");
const detectLocationBtn = document.getElementById("detectLocationBtn");
const findShopsBtn = document.getElementById("findShopsBtn");
const shopCategoryChips = document.getElementById("shopCategoryChips");
const geoStatusMessage = document.getElementById("geoStatusMessage");
const shopsPromptState = document.getElementById("shopsPromptState");
const shopsResultsArea = document.getElementById("shopsResultsArea");
const displayLocationText = document.getElementById("displayLocationText");
const displayCategoryBadge = document.getElementById("displayCategoryBadge");
const btnPrimaryGoogleMaps = document.getElementById("btnPrimaryGoogleMaps");
const btnSecondaryOsm = document.getElementById("btnSecondaryOsm");
const btnDirectionsMaps = document.getElementById("btnDirectionsMaps");
const supplyGuideGrid = document.getElementById("supplyGuideGrid");

let currentShopCategory = "all";

async function executeNearbyShopSearch() {
    if (!shopLocationInput) return;

    const loc = shopLocationInput.value.trim();
    if (!loc) {
        if (geoStatusMessage) {
            geoStatusMessage.textContent = "⚠️ Please enter a city, town, village name, or postal PIN code.";
            geoStatusMessage.style.color = "#dc2626";
        }
        shopLocationInput.focus();
        return;
    }

    if (geoStatusMessage) {
        geoStatusMessage.textContent = "🔍 Loading verified map options...";
        geoStatusMessage.style.color = "#166534";
    }

    try {
        const queryUrl = `http://127.0.0.1:5000/shops/search?location=${encodeURIComponent(loc)}&category=${encodeURIComponent(currentShopCategory)}`;
        const response = await fetch(queryUrl);
        const data = await response.json();

        if (!response.ok || data.status !== "success") {
            throw new Error(data.message || `HTTP ${response.status}: Failed to search nearby shops.`);
        }

        // Display results
        if (displayLocationText) displayLocationText.textContent = data.location;
        if (displayCategoryBadge) displayCategoryBadge.textContent = data.selected_category.name;

        if (btnPrimaryGoogleMaps) btnPrimaryGoogleMaps.href = data.primary_links.google_maps;
        if (btnSecondaryOsm) btnSecondaryOsm.href = data.primary_links.openstreetmap;
        if (btnDirectionsMaps) btnDirectionsMaps.href = data.primary_links.directions;

        // Render supply guide grid
        if (supplyGuideGrid && Array.isArray(data.all_category_links)) {
            supplyGuideGrid.innerHTML = data.all_category_links.map(cat => `
                <div class="supply-guide-card">
                    <div>
                        <div class="supply-card-header">
                            <span class="supply-card-icon">${cat.icon}</span>
                            <div>
                                <h4 class="supply-card-title">${escapeHtml(cat.name)}</h4>
                                ${cat.hindi_name ? `<p class="supply-card-hindi">${escapeHtml(cat.hindi_name)}</p>` : ""}
                            </div>
                        </div>
                        <p class="supply-card-desc" style="margin-top: 10px;">${escapeHtml(cat.description)}</p>
                    </div>
                    <div class="supply-card-action">
                        <span style="font-size: 0.78rem; color: #6b7280;">External Maps Query</span>
                        <a href="${escapeHtml(cat.google_maps_url)}" target="_blank" rel="noopener noreferrer" class="btn-supply-map">
                            Open in Maps ↗
                        </a>
                    </div>
                </div>
            `).join("");
        }

        if (shopsPromptState) shopsPromptState.classList.add("hidden");
        if (shopsResultsArea) shopsResultsArea.classList.remove("hidden");
        if (geoStatusMessage) geoStatusMessage.textContent = "";

    } catch (err) {
        console.error("Shop search error:", err);
        if (geoStatusMessage) {
            geoStatusMessage.textContent = `⚠️ Error: ${err.message || "Could not generate map search links."}`;
            geoStatusMessage.style.color = "#dc2626";
        }
    }
}

function initShopsPage() {
    if (!shopLocationInput) return;

    if (findShopsBtn) {
        findShopsBtn.addEventListener("click", executeNearbyShopSearch);
    }

    shopLocationInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            executeNearbyShopSearch();
        }
    });

    shopLocationInput.addEventListener("input", () => {
        const hasText = shopLocationInput.value.trim().length > 0;
        if (clearLocationBtn) {
            clearLocationBtn.style.display = hasText ? "inline-block" : "none";
        }
    });

    if (clearLocationBtn) {
        clearLocationBtn.addEventListener("click", () => {
            shopLocationInput.value = "";
            clearLocationBtn.style.display = "none";
            if (geoStatusMessage) geoStatusMessage.textContent = "";
            if (shopsResultsArea) shopsResultsArea.classList.add("hidden");
            if (shopsPromptState) shopsPromptState.classList.remove("hidden");
            shopLocationInput.focus();
        });
    }

    if (detectLocationBtn) {
        detectLocationBtn.addEventListener("click", () => {
            if (!navigator.geolocation) {
                if (geoStatusMessage) {
                    geoStatusMessage.textContent = "ℹ️ Geolocation is not supported by your browser. Please type your city or PIN code.";
                    geoStatusMessage.style.color = "#dc2626";
                }
                return;
            }

            detectLocationBtn.disabled = true;
            detectLocationBtn.textContent = "⏳ Detecting location...";
            if (geoStatusMessage) {
                geoStatusMessage.textContent = "Requesting optional device location...";
                geoStatusMessage.style.color = "#166534";
            }

            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    detectLocationBtn.disabled = false;
                    detectLocationBtn.textContent = "🎯 Use My Location (Optional)";
                    const coords = `${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`;
                    shopLocationInput.value = coords;
                    if (clearLocationBtn) clearLocationBtn.style.display = "inline-block";
                    if (geoStatusMessage) {
                        geoStatusMessage.textContent = "✓ Device coordinates detected (Optional). Click 'Find Nearby Shops' to view local stores.";
                        geoStatusMessage.style.color = "#166534";
                    }
                    executeNearbyShopSearch();
                },
                (err) => {
                    detectLocationBtn.disabled = false;
                    detectLocationBtn.textContent = "🎯 Use My Location (Optional)";
                    let errMsg = "Location permission denied or timed out. Please enter your city, town, or PIN code manually.";
                    if (err.code === 1) errMsg = "Location permission was denied. You can still type your town name or PIN code.";
                    if (geoStatusMessage) {
                        geoStatusMessage.textContent = `ℹ️ ${errMsg}`;
                        geoStatusMessage.style.color = "#b45309";
                    }
                },
                { timeout: 10000, maximumAge: 60000 }
            );
        });
    }

    if (shopCategoryChips) {
        shopCategoryChips.addEventListener("click", (e) => {
            const chip = e.target.closest(".shop-chip");
            if (!chip) return;

            shopCategoryChips.querySelectorAll(".shop-chip").forEach(c => c.classList.remove("active"));
            chip.classList.add("active");

            currentShopCategory = chip.getAttribute("data-category") || "all";
            if (shopLocationInput.value.trim().length > 0) {
                executeNearbyShopSearch();
            }
        });
    }
}

// =========================================
// Multilingual Support & Language Switcher
// =========================================

function initLanguageSelector() {
    if (typeof document === "undefined") return;
    const langSelect = document.getElementById("languageSelector");
    const currentLang = typeof getCurrentLanguage === "function" ? getCurrentLanguage() : "en";

    if (langSelect) {
        langSelect.value = currentLang;
        langSelect.addEventListener("change", (e) => {
            const chosen = e.target.value;
            if (typeof setLanguage === "function") {
                setLanguage(chosen);
            }
        });
    }

    // Listen for custom event dispatched by setLanguage()
    if (typeof window !== "undefined" && typeof window.addEventListener === "function") {
        window.addEventListener("cropcureLanguageChanged", (e) => {
            const newLang = (e.detail && e.detail.lang) || "en";
            if (langSelect) {
                langSelect.value = newLang;
            }

            // 1. Re-render active diagnosis if present
            if (currentPrediction) {
                displayPredictionResult(currentPrediction);
            }

            // 2. Re-render government schemes if loaded
            if (typeof schemesGridContainer !== "undefined" && schemesGridContainer && typeof allGovernmentSchemes !== "undefined" && allGovernmentSchemes && allGovernmentSchemes.length > 0) {
                renderGovernmentSchemes();
            }
        });
    }

    // Initial translation application
    if (typeof applyTranslations === "function") {
        applyTranslations(currentLang);
    }
}

// =========================================
// Agriculture Expert Support & Consultation Summary (Step 7)
// =========================================

function initExpertsPage() {
    if (typeof document === "undefined") return;

    const expertLocationInput = document.getElementById("expertLocationInput");
    const detectExpertLocationBtn = document.getElementById("detectExpertLocationBtn");
    const clearExpertLocationBtn = document.getElementById("clearExpertLocationBtn");
    const findExpertsBtn = document.getElementById("findExpertsBtn");
    const expertGeoStatus = document.getElementById("expertGeoStatus");
    const expertsResultsArea = document.getElementById("expertsResultsArea");
    const expertLocationDisplay = document.getElementById("expertLocationDisplay");
    const btnMapsKvk = document.getElementById("btnMapsKvk");
    const btnMapsDept = document.getElementById("btnMapsDept");
    const btnPortalKvk = document.getElementById("btnPortalKvk");

    // Location search execution
    const executeExpertSearch = async () => {
        if (!expertLocationInput) return;
        const loc = expertLocationInput.value.trim();
        if (!loc) {
            if (expertGeoStatus) {
                expertGeoStatus.textContent = "⚠️ Please enter a district, town, city, or PIN code.";
                expertGeoStatus.style.color = "#dc2626";
            }
            expertLocationInput.focus();
            return;
        }

        if (expertGeoStatus) {
            expertGeoStatus.textContent = "🔍 Loading KVK and extension office links...";
            expertGeoStatus.style.color = "#166534";
        }

        try {
            const queryUrl = `http://127.0.0.1:5000/experts/search?location=${encodeURIComponent(loc)}`;
            const response = await fetch(queryUrl);
            const data = await response.json();

            if (!response.ok || data.status !== "success") {
                throw new Error(data.message || `HTTP ${response.status}: Failed to search extension offices.`);
            }

            if (expertLocationDisplay) expertLocationDisplay.textContent = data.location;
            if (btnMapsKvk) btnMapsKvk.href = data.primary_links.google_maps_kvk;
            if (btnMapsDept) btnMapsDept.href = data.primary_links.google_maps_dept;
            if (btnPortalKvk) btnPortalKvk.href = data.primary_links.icar_kvk_portal;

            if (expertsResultsArea) expertsResultsArea.classList.remove("hidden");
            if (expertGeoStatus) expertGeoStatus.textContent = "";

        } catch (err) {
            console.error("Expert search error:", err);
            if (expertGeoStatus) {
                expertGeoStatus.textContent = `⚠️ Error: ${err.message || "Could not generate expert search links."}`;
                expertGeoStatus.style.color = "#dc2626";
            }
        }
    };

    if (findExpertsBtn) {
        findExpertsBtn.addEventListener("click", executeExpertSearch);
    }

    if (expertLocationInput) {
        expertLocationInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                executeExpertSearch();
            }
        });

        expertLocationInput.addEventListener("input", () => {
            const hasText = expertLocationInput.value.trim().length > 0;
            if (clearExpertLocationBtn) {
                clearExpertLocationBtn.style.display = hasText ? "inline-block" : "none";
            }
        });
    }

    if (clearExpertLocationBtn) {
        clearExpertLocationBtn.addEventListener("click", () => {
            if (expertLocationInput) {
                expertLocationInput.value = "";
                expertLocationInput.focus();
            }
            clearExpertLocationBtn.style.display = "none";
            if (expertGeoStatus) expertGeoStatus.textContent = "";
            if (expertsResultsArea) expertsResultsArea.classList.add("hidden");
        });
    }

    if (detectExpertLocationBtn && typeof navigator !== "undefined" && navigator.geolocation) {
        detectExpertLocationBtn.addEventListener("click", () => {
            detectExpertLocationBtn.disabled = true;
            detectExpertLocationBtn.textContent = "⏳ Detecting location...";
            if (expertGeoStatus) {
                expertGeoStatus.textContent = "Requesting optional device location...";
                expertGeoStatus.style.color = "#166534";
            }

            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    detectExpertLocationBtn.disabled = false;
                    detectExpertLocationBtn.textContent = "🎯 Use My Location (Optional)";
                    const coords = `${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`;
                    if (expertLocationInput) {
                        expertLocationInput.value = coords;
                        if (clearExpertLocationBtn) clearExpertLocationBtn.style.display = "inline-block";
                    }
                    if (expertGeoStatus) {
                        expertGeoStatus.textContent = "✓ Device coordinates detected (Optional).";
                        expertGeoStatus.style.color = "#166534";
                    }
                    executeExpertSearch();
                },
                (err) => {
                    detectExpertLocationBtn.disabled = false;
                    detectExpertLocationBtn.textContent = "🎯 Use My Location (Optional)";
                    if (expertGeoStatus) {
                        expertGeoStatus.textContent = "ℹ️ Location access not granted. Please enter your district or PIN code manually.";
                        expertGeoStatus.style.color = "#b45309";
                    }
                },
                { timeout: 10000, maximumAge: 60000 }
            );
        });
    }

    // -------------------------------------------------------------------------
    // Consultation Summary Generator
    // -------------------------------------------------------------------------
    const summaryDate = document.getElementById("summaryDate");
    const summaryCrop = document.getElementById("summaryCrop");
    const summaryDisease = document.getElementById("summaryDisease");
    const summaryConfidence = document.getElementById("summaryConfidence");
    const summarySeverity = document.getElementById("summarySeverity");
    const summarySymptoms = document.getElementById("summarySymptoms");
    const summaryOutput = document.getElementById("consultationSummaryOutput");
    const generateSummaryBtn = document.getElementById("generateSummaryBtn");
    const copySummaryBtn = document.getElementById("copySummaryBtn");
    const copyToast = document.getElementById("copyToast");
    const summaryAutoLoadedNote = document.getElementById("summaryAutoLoadedNote");

    if (!summaryOutput) return;

    // Set today's date if empty
    if (summaryDate && typeof summaryDate.value === "string" && !summaryDate.value) {
        summaryDate.value = new Date().toISOString().split("T")[0];
    }

    // Check if recent diagnosis exists in sessionStorage
    let lastDiag = null;
    try {
        if (typeof sessionStorage !== "undefined") {
            const stored = sessionStorage.getItem("cropcure_last_diagnosis");
            if (stored) lastDiag = JSON.parse(stored);
        }
    } catch (e) {}

    if (lastDiag) {
        const dName = lastDiag.predicted_class || lastDiag.prediction || "";
        const cVal = Number(lastDiag.confidence || 0);
        const cPct = (cVal * 100).toFixed(1) + "%";
        const isLow = cVal < 0.50;

        // Extract crop name
        let crop = "Tomato";
        if (dName.toLowerCase().startsWith("apple")) crop = "Apple";
        else if (dName.toLowerCase().startsWith("corn")) crop = "Corn (Maize)";
        else if (dName.toLowerCase().startsWith("potato")) crop = "Potato";
        else if (dName.toLowerCase().startsWith("grape")) crop = "Grape";

        if (summaryCrop && typeof summaryCrop.value === "string" && !summaryCrop.value) summaryCrop.value = crop;
        if (summaryDisease && typeof summaryDisease.value === "string" && !summaryDisease.value) {
            summaryDisease.value = (typeof translateDisease === "function") ? translateDisease(dName) : formatDiseaseName(dName);
        }
        if (summaryConfidence && typeof summaryConfidence.value === "string" && !summaryConfidence.value) {
            summaryConfidence.value = isLow ? `${cPct} (Uncertain Visual Diagnosis < 50%)` : `${cPct} (High Visual Confidence)`;
        }
        if (summaryAutoLoadedNote && summaryAutoLoadedNote.classList) {
            summaryAutoLoadedNote.classList.remove("hidden");
        }
    }

    // Format summary output
    const buildSummaryText = () => {
        const dateVal = (summaryDate && typeof summaryDate.value === "string" && summaryDate.value.trim()) ? summaryDate.value.trim() : new Date().toISOString().split("T")[0];
        const cropVal = (summaryCrop && typeof summaryCrop.value === "string" && summaryCrop.value.trim()) ? summaryCrop.value.trim() : "Unspecified Crop";
        const diseaseVal = (summaryDisease && typeof summaryDisease.value === "string" && summaryDisease.value.trim()) ? summaryDisease.value.trim() : "Preliminary Visual Match";
        const confVal = (summaryConfidence && typeof summaryConfidence.value === "string" && summaryConfidence.value.trim()) ? summaryConfidence.value.trim() : "Not specified";
        const sevVal = (summarySeverity && typeof summarySeverity.value === "string" && summarySeverity.value.trim()) ? summarySeverity.value.trim() : "Moderate";
        const symVal = (summarySymptoms && typeof summarySymptoms.value === "string" && summarySymptoms.value.trim()) ? summarySymptoms.value.trim() : "Visual leaf symptoms observed in field; awaiting expert confirmation.";

        return [
            "===========================================================",
            "CROPCURE AI - FARMER FIELD CONSULTATION SUMMARY",
            "===========================================================",
            `Date: ${dateVal}`,
            `Crop: ${cropVal}`,
            `Suspected / Visual Diagnosis: ${diseaseVal}`,
            `Visual Model Confidence: ${confVal}`,
            `Severity / Spread in Field: ${sevVal}`,
            "",
            "OBSERVED FIELD & LEAF SYMPTOMS:",
            symVal,
            "",
            "-----------------------------------------------------------",
            "IMPORTANT NOTICE FOR AGRICULTURAL EXPERT / KVK SCIENTIST:",
            "- Visual predictions are preliminary machine-learning assessments.",
            "- Please perform physical/laboratory examination to confirm diagnosis.",
            "- Confirm target pathogen before prescribing chemical fungicides or pesticides.",
            "Kisan Call Centre (Toll-Free Helpline): 1800-180-1551 (6 AM - 10 PM)",
            "==========================================================="
        ].join("\n");
    };

    // Update preview
    const updateSummaryPreview = () => {
        const text = buildSummaryText();
        if (summaryOutput) {
            summaryOutput.textContent = text;
        }
    };

    updateSummaryPreview();

    if (generateSummaryBtn) {
        generateSummaryBtn.addEventListener("click", updateSummaryPreview);
    }

    if (copySummaryBtn) {
        copySummaryBtn.addEventListener("click", async () => {
            const text = buildSummaryText();
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(text);
                } else {
                    const tempTa = document.createElement("textarea");
                    tempTa.value = text;
                    document.body.appendChild(tempTa);
                    tempTa.select();
                    document.execCommand("copy");
                    document.body.removeChild(tempTa);
                }

                if (copyToast) {
                    copyToast.classList.remove("hidden");
                    setTimeout(() => {
                        copyToast.classList.add("hidden");
                    }, 3500);
                }
            } catch (err) {
                console.error("Clipboard copy error:", err);
                alert("Could not automatically copy to clipboard. Please select and copy the text manually from the preview box.");
            }
        });
    }
}

// Automatically load page components when DOM is ready
function initPage() {
    initLanguageSelector();
    fetchEvaluationMetrics();
    fetchGovernmentSchemes();
    initShopsPage();
    initExpertsPage();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPage);
} else {
    initPage();
}