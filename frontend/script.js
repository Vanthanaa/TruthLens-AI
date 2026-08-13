// TruthLens AI - Premium Frontend JavaScript

document.addEventListener("DOMContentLoaded", () => {
    // Smooth scroll & scroll-top button
    const scrollTopBtn = document.getElementById("scrollTop");
    if (scrollTopBtn) {
        window.addEventListener("scroll", () => {
            if (window.scrollY > 250) {
                scrollTopBtn.style.display = "flex";
            } else {
                scrollTopBtn.style.display = "none";
            }
        });

        scrollTopBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // Animated counters on hero section
    const counters = document.querySelectorAll(".counter");
    const animateCounters = () => {
        counters.forEach(counter => {
            const target = +counter.getAttribute("data-target");
            let current = 0;
            const increment = target / 80;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    counter.textContent = Math.round(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };
            updateCounter();
        });
    };

    // Trigger counters when in viewport
    const heroSection = document.querySelector(".hero-section");
    if (heroSection && counters.length) {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounters();
                    observer.disconnect();
                }
            });
        }, { threshold: 0.4 });

        observer.observe(heroSection);
    }

    /* Toast Helper */
    const showToast = (message, type = "info") => {
        let container = document.querySelector(".toast-container");
        if (!container) {
            container = document.createElement("div");
            container.className = "toast-container";
            document.body.appendChild(container);
        }

        const toast = document.createElement("div");
        toast.className = "custom-toast p-3 mt-2 d-flex align-items-center justify-content-between";

        const iconMap = {
            success: "fa-check-circle",
            error: "fa-times-circle",
            info: "fa-info-circle",
            warning: "fa-exclamation-triangle"
        };
        const colorMap = {
            success: "#22c55e",
            error: "#ef4444",
            info: "#3b82f6",
            warning: "#facc15"
        };

        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas ${iconMap[type]} me-2" style="color:${colorMap[type]}"></i>
                <span>${message}</span>
            </div>
            <button class="btn btn-sm btn-outline-light ms-3">Close</button>
        `;

        const closeBtn = toast.querySelector("button");
        closeBtn.addEventListener("click", () => {
            toast.remove();
        });

        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 4000);
    };

    /* Upload Page Logic */
    const uploadArea = document.getElementById("uploadArea");
    const fileInput = document.getElementById("fileInput");
    const filePreview = document.getElementById("filePreview");
    const fileNameEl = document.getElementById("fileName");
    const fileSizeEl = document.getElementById("fileSize");
    const uploadProgress = document.getElementById("uploadProgress");
    const uploadStatus = document.getElementById("uploadStatus");
    const removeFileBtn = document.getElementById("removeFile");
    const analyzeSection = document.getElementById("analyzeSection");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const loadingSection = document.getElementById("loadingSection");
    const loadingText = document.getElementById("loadingText");
    const step1 = document.getElementById("step1");
    const step2 = document.getElementById("step2");
    const step3 = document.getElementById("step3");
    const step4 = document.getElementById("step4");

    let currentFile = null;

    if (uploadArea && fileInput) {
        const openFileDialog = () => fileInput.click();

        uploadArea.addEventListener("click", openFileDialog);

        uploadArea.addEventListener("dragover", (e) => {
            e.preventDefault();
            uploadArea.classList.add("drag-over");
        });

        uploadArea.addEventListener("dragleave", () => {
            uploadArea.classList.remove("drag-over");
        });

        uploadArea.addEventListener("drop", (e) => {
            e.preventDefault();
            uploadArea.classList.remove("drag-over");
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFile(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFile(e.target.files[0]);
            }
        });

        const handleFile = (file) => {
            currentFile = file;
            filePreview.style.display = "block";
            analyzeSection.style.display = "block";
            uploadProgress.style.width = "0%";
            uploadStatus.textContent = "Preparing upload...";

            fileNameEl.textContent = file.name;
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            fileSizeEl.textContent = `${sizeMB} MB`;

            // Fake upload progress animation
            let progress = 0;
            const interval = setInterval(() => {
                progress += 8;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    uploadStatus.textContent = "File ready for analysis";
                    showToast("File uploaded successfully. Ready for analysis.", "success");
                }
                uploadProgress.style.width = `${progress}%`;
            }, 120);
        };

        if (removeFileBtn) {
            removeFileBtn.addEventListener("click", () => {
                currentFile = null;
                filePreview.style.display = "none";
                analyzeSection.style.display = "none";
                uploadProgress.style.width = "0%";
                uploadStatus.textContent = "Preparing upload...";
            });
        }
    }

    if (analyzeBtn && loadingSection) {
        analyzeBtn.addEventListener("click", () => {
            if (!currentFile) {
                showToast("Please upload a file before analysis.", "warning");
                return;
            }

            analyzeSection.style.display = "none";
            loadingSection.style.display = "block";
            loadingText.textContent = "Running multi-modal detection algorithms";

            // Simulated step-wise analysis
            const steps = [step1, step2, step3, step4];
            let index = 0;

            const runSteps = () => {
                if (index > 0 && steps[index - 1]) {
                    steps[index - 1].classList.remove("active");
                }
                if (steps[index]) {
                    steps[index].classList.add("active");
                }

                index++;
                if (index < steps.length + 1) {
                    setTimeout(runSteps, 900);
                } else {
                    // After analysis, redirect to result page
                    setTimeout(() => {
                        loadingText.textContent = "Generating report...";
                        setTimeout(() => {
                            window.location.href = "result.html";
                        }, 800);
                    }, 600);
                }
            };
            runSteps();
        });
    }

    /* Result Page Logic */
    const overallScoreBar = document.getElementById("overallScore");
    const overallScoreText = document.getElementById("overallScoreText");

    if (overallScoreBar && overallScoreText) {
        const targetScore = parseInt(overallScoreBar.getAttribute("data-value"), 10) || 90;
        let current = 0;

        const animateScore = () => {
            current += 2;
            if (current >= targetScore) {
                current = targetScore;
            } else {
                requestAnimationFrame(animateScore);
            }
            overallScoreBar.style.width = `${current}%`;
            overallScoreText.textContent = `${current}%`;
        };

        // Animate when in view
        const resultSection = document.querySelector(".result-section");
        if (resultSection) {
            const observer = new IntersectionObserver(entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateScore();
                        observer.disconnect();
                    }
                });
            }, { threshold: 0.4 });
            observer.observe(resultSection);
        } else {
            animateScore();
        }
    }

    const downloadReportBtn = document.getElementById("downloadReport");
    if (downloadReportBtn) {
        downloadReportBtn.addEventListener("click", () => {
            showToast("PDF report generation is simulated in this UI. Integrate backend to export actual PDF.", "info");
        });
    }

    const fileComplaintBtn = document.getElementById("fileComplaint");
    if (fileComplaintBtn) {
        fileComplaintBtn.addEventListener("click", () => {
            window.location.href = "complaint.html";
        });
    }

    /* Complaint Page Logic */
    const complaintForm = document.getElementById("complaintForm");
    const evidenceUpload = document.getElementById("evidenceUpload");
    const evidenceInput = document.getElementById("evidenceInput");
    const evidenceList = document.getElementById("evidenceList");
    const complaintIdEl = document.getElementById("complaintId");
    const downloadComplaintBtn = document.getElementById("downloadComplaint");

    if (evidenceUpload && evidenceInput && evidenceList) {
        evidenceUpload.addEventListener("click", () => evidenceInput.click());

        evidenceInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files.length > 0) {
                Array.from(e.target.files).forEach(file => {
                    const item = document.createElement("div");
                    item.className = "evidence-item";
                    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                    item.innerHTML = `
                        <span><i class="fas fa-file-alt me-2 text-primary"></i>${file.name} (${sizeMB} MB)</span>
                        <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
                    `;
                    const removeBtn = item.querySelector("button");
                    removeBtn.addEventListener("click", () => item.remove());
                    evidenceList.appendChild(item);
                });
                showToast("Evidence file added to complaint.", "success");
            }
        });
    }

    if (complaintForm) {
        complaintForm.addEventListener("submit", (e) => {
            e.preventDefault();

            // Basic client-side validation can be extended here
            const name = document.getElementById("fullName").value.trim();
            const email = document.getElementById("email").value.trim();

            if (!name || !email) {
                showToast("Please fill all required fields.", "error");
                return;
            }

            // Generate fake complaint ID
            const rand = Math.floor(10000 + Math.random() * 90000);
            const complaintId = `TL-2026-${rand}`;
            if (complaintIdEl) {
                complaintIdEl.textContent = complaintId;
            }

            // Show success modal
            const successModalEl = document.getElementById("successModal");
            if (successModalEl) {
                const modal = new bootstrap.Modal(successModalEl);
                modal.show();
            }

            showToast("Complaint submitted successfully. Check your email for confirmation.", "success");
            complaintForm.reset();
            if (evidenceList) evidenceList.innerHTML = "";
        });
    }

    if (downloadComplaintBtn) {
        downloadComplaintBtn.addEventListener("click", () => {
            showToast("Complaint receipt download is simulated. Integrate backend/PDF export for production.", "info");
        });
    }
});
