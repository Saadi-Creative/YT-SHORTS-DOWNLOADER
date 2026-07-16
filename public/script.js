document.addEventListener("DOMContentLoaded", () => {
    const urlInput = document.getElementById("urlInput");
    const downloadBtn = document.getElementById("downloadBtn");
    const btnText = document.querySelector(".btn-text");
    const btnSpinner = document.querySelector(".btn-spinner");
    
    const statusArea = document.getElementById("statusArea");
    const progressContainer = document.getElementById("progressContainer");
    const progressBar = document.getElementById("progressBar");
    const progressPercent = document.getElementById("progressPercent");
    const progressSize = document.getElementById("progressSize");
    const progressSpeed = document.getElementById("progressSpeed");
    const statusMessage = document.getElementById("statusMessage");
    
    const successArea = document.getElementById("successArea");
    const directDownloadLink = document.getElementById("directDownloadLink");

    let eventSource = null;

    function resetUI() {
        successArea.classList.add("hidden");
        statusArea.classList.add("hidden");
        progressContainer.classList.add("hidden");
        statusMessage.classList.remove("error");
        statusMessage.textContent = "Starting...";
        progressBar.style.width = "0%";
        progressPercent.textContent = "0%";
        progressSize.textContent = "0 MB";
        progressSpeed.textContent = "0 KB/s";
    }

    function setLoading(isLoading) {
        if (isLoading) {
            urlInput.disabled = true;
            downloadBtn.disabled = true;
            btnText.classList.add("hidden");
            btnSpinner.classList.remove("hidden");
        } else {
            urlInput.disabled = false;
            downloadBtn.disabled = false;
            btnText.classList.remove("hidden");
            btnSpinner.classList.add("hidden");
        }
    }

    downloadBtn.addEventListener("click", () => {
        const url = urlInput.value.trim();
        if (!url) return;

        // Basic check to see if it's a URL
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            alert("Please enter a valid URL");
            return;
        }

        if (eventSource) {
            eventSource.close();
        }

        resetUI();
        setLoading(true);
        statusArea.classList.remove("hidden");

        const apiUrl = `/api/download?url=${encodeURIComponent(url)}`;
        eventSource = new EventSource(apiUrl);

        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);

                switch (data.status) {
                    case "starting":
                        statusMessage.textContent = data.message;
                        break;
                    case "downloading":
                        progressContainer.classList.remove("hidden");
                        statusMessage.textContent = "Downloading high-quality video & audio...";
                        
                        // Parse percent string like "45.2%"
                        const percentRaw = data.percent.replace("%", "");
                        progressBar.style.width = data.percent;
                        progressPercent.textContent = data.percent;
                        progressSize.textContent = data.size;
                        progressSpeed.textContent = data.speed;
                        break;
                    case "processing":
                        progressContainer.classList.add("hidden");
                        statusMessage.textContent = data.message;
                        break;
                    case "uploading":
                        statusMessage.textContent = data.message;
                        break;
                    case "done":
                        setLoading(false);
                        statusArea.classList.add("hidden");
                        successArea.classList.remove("hidden");
                        eventSource.close();
                        
                        // Automatically trigger download
                        const a = document.createElement("a");
                        a.href = data.url;
                        // Use original title for filename
                        a.download = data.title ? `${data.title}.mp4` : "ShortsVideo.mp4"; 
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        break;
                    case "error":
                        setLoading(false);
                        progressContainer.classList.add("hidden");
                        statusMessage.classList.add("error");
                        statusMessage.textContent = `Error: ${data.message}`;
                        eventSource.close();
                        break;
                }
            } catch (err) {
                console.error("Failed to parse SSE message", err);
            }
        };

        eventSource.onerror = function(err) {
            console.error("EventSource failed:", err);
            // Ignore temporary connection drops, but if it completely fails:
            setLoading(false);
            statusMessage.classList.add("error");
            statusMessage.textContent = "Connection lost. Please try again.";
            eventSource.close();
        };
    });

    directDownloadLink.addEventListener("click", (e) => {
        e.preventDefault();
        urlInput.value = "";
        resetUI();
    });
});
