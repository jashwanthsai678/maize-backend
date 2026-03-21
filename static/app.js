document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const uploadArea = document.getElementById('upload-area');
    const imageInput = document.getElementById('image-input');
    const imagePreview = document.getElementById('image-preview');
    const uploadContent = document.getElementById('upload-content');
    const contextToggle = document.getElementById('context-toggle');
    const accordion = document.querySelector('.accordion');
    const form = document.getElementById('advisory-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');
    
    // Result Elements
    const emptyState = document.getElementById('empty-state');
    const resultsContent = document.getElementById('results-content');
    
    let selectedFile = null;

    // --- Accordion Logic ---
    contextToggle.addEventListener('click', () => {
        accordion.classList.toggle('active');
    });

    // --- Drag and Drop Logic ---
    uploadArea.addEventListener('click', () => imageInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    imageInput.addEventListener('change', function() {
        if (this.files.length) {
            handleFile(this.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file.');
            return;
        }
        
        selectedFile = file;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            uploadContent.style.display = 'none';
            uploadArea.style.padding = '0';
            uploadArea.style.border = 'none';
            submitBtn.disabled = false;
        }
        reader.readAsDataURL(file);
    }

    // --- Form Submission Logic ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // UI State: Loading
        submitBtn.disabled = true;
        document.querySelector('.spinner').style.display = 'block';
        document.querySelector('.btn-text').innerText = 'AI is thinking...';

        const formData = new FormData();
        formData.append("image", document.getElementById('image-input').files[0]);
        formData.append("district", document.getElementById('district').value);
        formData.append("season", document.getElementById('season').value);
        formData.append("crop_year", document.getElementById('crop_year').value);
        formData.append("area_ha", document.getElementById('area_ha').value);
        formData.append("growth_stage", document.getElementById('growth_stage').value);
        formData.append("language", document.getElementById('language').value);

        try {
            // We call our Render orchestrator, which then handles the cloud coordination
            const response = await fetch('/orchestrate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                const errorMsg = data.detail || data.error || `Server error: ${response.status}`;
                throw new Error(errorMsg);
            }

            // Reveal the Results section
            document.getElementById('empty-state').style.display = 'none';
            document.getElementById('results-content').style.display = 'block';
            
            // Populate labels
            document.getElementById('res-diagnosis').innerText = data.detected_pest;
            document.getElementById('res-yield').innerText = (typeof data.yield_prediction === 'number') 
                ? data.yield_prediction.toFixed(2) 
                : (data.yield_prediction || "0.00");
            
            document.getElementById('res-advisory').innerHTML = `<p>${data.advisory}</p>`;
            
            // Update and Animate confidence bar
            const rawConf = data.detection_confidence || 0;
            const percentageNum = Math.round(rawConf <= 1 ? rawConf * 100 : rawConf);
            const percentage = percentageNum + '%';
            
            document.getElementById('res-confidence-bar').style.width = '0%';
            setTimeout(() => {
                document.getElementById('res-confidence-bar').style.width = percentage;
            }, 100);
            document.getElementById('res-confidence-text').innerText = percentage;

            // Severity Badge (if provided)
            const badge = document.getElementById('severity-badge');
            if (data.severity) {
                const sev = data.severity.toLowerCase();
                badge.innerText = sev.charAt(0).toUpperCase() + sev.slice(1) + " Severity";
                badge.className = `badge ${sev}`;
            }

            // Image Update (Annotated if available)
            const img = document.getElementById('result-image');
            if (data.visual_diagnosis && data.visual_diagnosis.annotated_image_base64) {
                 img.src = `data:image/jpeg;base64,${data.visual_diagnosis.annotated_image_base64}`;
            } else {
                 img.src = imagePreview.src;
            }

            // District/Season labels
            document.getElementById('res-district').innerText = document.getElementById('district').value;
            document.getElementById('res-season').innerText = document.getElementById('season').value;

        } catch (err) {
            alert("Analysis Error: " + err.message);
            console.error(err);
            emptyState.style.display = 'flex';
        } finally {
            submitBtn.disabled = false;
            document.querySelector('.spinner').style.display = 'none';
            document.querySelector('.btn-text').innerText = 'Generate Advisory';
        }
    });

    // --- Image Preview Logic ---
    imageInput.addEventListener('change', function(e) {
        if (!this.files.length) return;
        const reader = new FileReader();
        reader.onload = function() {
            imagePreview.src = reader.result;
            imagePreview.style.display = 'block';
            uploadContent.style.display = 'none';
            uploadArea.style.padding = '0';
            uploadArea.style.border = 'none';
            submitBtn.disabled = false;
        }
        reader.readAsDataURL(e.target.files[0]);
    });
});
