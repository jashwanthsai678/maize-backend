// static/app.js

const form = document.getElementById('advisory-form');
const submitBtn = document.getElementById('submit-btn');
const imageInput = document.getElementById('image-input');

// 1. Handle Image Selection & Preview
document.getElementById('upload-area').onclick = () => imageInput.click();

imageInput.addEventListener('change', function(e) {
    if (this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('image-preview');
            preview.src = e.target.result;
            preview.style.display = 'block';
            document.getElementById('upload-content').style.display = 'none';
            // Also styling for the upload area
            const uploadArea = document.getElementById('upload-area');
            uploadArea.style.padding = '0';
            uploadArea.style.border = 'none';
            submitBtn.disabled = false; // Enable button once image is present
        }
        reader.readAsDataURL(this.files[0]);
    }
});

// 2. Handle Form Submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // UI State: Loading
    submitBtn.disabled = true;
    document.querySelector('.spinner').style.display = 'block';
    document.querySelector('.btn-text').innerText = 'AI Analysis in Progress...';

    // Prepare Multipart Data
    const formData = new FormData();
    formData.append("image", imageInput.files[0]);
    formData.append("district", document.getElementById('district').value);
    formData.append("season", document.getElementById('season').value);
    formData.append("crop_year", document.getElementById('crop_year').value);
    formData.append("area_ha", document.getElementById('area_ha').value);
    formData.append("growth_stage", document.getElementById('growth_stage').value);
    formData.append("language", document.getElementById('language').value);
    
    // Add the hidden weather data from the HTML script tag
    formData.append("weather_json", JSON.stringify(window.weatherData));

    try {
        // We call the Orchestrator on Render
        const response = await fetch('/orchestrate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Orchestration failed');

        const data = await response.json();

        // 3. Update the UI with results from both VMs
        document.getElementById('empty-state').style.display = 'none';
        document.getElementById('results-content').style.display = 'block';

        // Set YOLO Results
        document.getElementById('res-diagnosis').innerText = data.detected_pest;
        
        // Confidence bar animation
        const rawConf = data.detection_confidence || 0;
        const confNum = Math.round(rawConf <= 1 ? rawConf * 100 : rawConf);
        const confPercent = confNum + '%';
        
        const bar = document.getElementById('res-confidence-bar');
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = confPercent;
        }, 100);
        document.getElementById('res-confidence-text').innerText = confPercent;
        
        // Severity Badge (if provided)
        const badge = document.getElementById('severity-badge');
        if (data.severity) {
            const sev = data.severity.toLowerCase();
            badge.innerText = sev.charAt(0).toUpperCase() + sev.slice(1) + " Severity";
            badge.className = `badge ${sev}`;
        }

        // Show Annotated Image if returned (Optional)
        if(data.visual_diagnosis && data.visual_diagnosis.annotated_image_base64) {
            document.getElementById('result-image').src = `data:image/jpeg;base64,${data.visual_diagnosis.annotated_image_base64}`;
        }

        // Set Yield Results
        const yVal = data.yield_prediction;
        document.getElementById('res-yield').innerText = (typeof yVal === 'number') ? yVal.toFixed(2) : (yVal || "0.00");
        document.getElementById('res-district').innerText = document.getElementById('district').value;
        document.getElementById('res-season').innerText = document.getElementById('season').value;

        // Set Qwen Advisory (Convert Markdown-like breaks to HTML)
        let advisoryText = data.advisory || "";
        advisoryText = advisoryText
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');
        
        document.getElementById('res-advisory').innerHTML = `<div class="advisory-text">${advisoryText}</div>`;

        // Scroll to results on mobile
        if(window.innerWidth < 900) {
            document.getElementById('results-content').scrollIntoView({ behavior: 'smooth' });
        }

    } catch (err) {
        console.error(err);
        alert("Error connecting to the AI System. Please check if VM 1 and VM 2 are running.");
    } finally {
        submitBtn.disabled = false;
        document.querySelector('.spinner').style.display = 'none';
        document.querySelector('.btn-text').innerText = 'Generate Advisory';
    }
});

// Accordion Toggle Logic
document.getElementById('context-toggle').onclick = function() {
    const content = document.getElementById('context-content');
    content.classList.toggle('active');
    // Rotate the arrow icon if it exists
    const icon = this.querySelector('i.fa-chevron-down');
    if (icon) icon.classList.toggle('rotate');
};
