document.addEventListener("DOMContentLoaded", function () {

    const button = document.getElementById("agentSearchButton");
    const queryInput = document.getElementById("agentQuery");
    const status = document.getElementById("agentStatus");
    const planBox = document.getElementById("agentPlan");

    if (!button || !queryInput || !status || !planBox) {
        console.error("JobScout AI: Required elements not found.");
        return;
    }

    button.addEventListener("click", async function () {

        const query = queryInput.value.trim();

        if (!query) {
            status.textContent = "Please describe the job you are looking for.";
            status.className = "agent-status error";
            queryInput.focus();
            return;
        }

        button.disabled = true;

        button.innerHTML = `
            <span class="agent-spinner"></span>
            <span>JobScout AI is thinking...</span>
        `;

        status.textContent =
            "Understanding your request and searching for relevant jobs...";

        status.className = "agent-status processing";

        planBox.innerHTML = "";
        planBox.classList.remove("visible", "success", "warning", "error");

        try {

            const response = await fetch("/api/agent-search", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    query: query
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || "AI search failed."
                );
            }

            if (data.status === "error") {
                throw new Error(
                    data.message || "AI search is unavailable."
                );
            }

            const totalJobs = Number(data.total_jobs || 0);

            let html = `
                <div class="analysis-header">

                    <div class="analysis-icon">
                        🧠
                    </div>

                    <div>
                        <div class="analysis-label">
                            AI SEARCH ANALYSIS
                        </div>

                        <h3>
                            JobScout understood your request
                        </h3>
                    </div>

                </div>

                <div class="request-preview">

                    <span>
                        YOUR REQUEST
                    </span>

                    <p>
                        ${escapeHTML(data.user_query || query)}
                    </p>

                </div>
            `;


            if (
                Array.isArray(data.user_skills) &&
                data.user_skills.length > 0
            ) {

                html += `
                    <div class="analysis-section">

                        <div class="analysis-section-title">
                            ⚙️ Detected skills
                        </div>

                        <div class="agent-skills">
                `;

                data.user_skills.forEach(function (skill) {

                    html += `
                        <span class="agent-skill">
                            ✓ ${escapeHTML(skill)}
                        </span>
                    `;

                });

                html += `
                        </div>

                    </div>
                `;

            }


            if (totalJobs > 0) {

                html += `
                    <div class="agent-result-summary success-summary">

                        <div class="summary-icon">
                            ✓
                        </div>

                        <div>

                            <strong>
                                ${totalJobs}
                                ${totalJobs === 1 ? "job" : "jobs"}
                                discovered
                            </strong>

                            <span>
                                Relevant opportunities were found.
                            </span>

                        </div>

                    </div>
                `;

                status.textContent =
                    "✓ AI search completed successfully.";

                status.className =
                    "agent-status success";

                planBox.classList.add("success");

            } else {

                html += `
                    <div class="agent-result-summary warning-summary">

                        <div class="summary-icon">
                            !
                        </div>

                        <div>

                            <strong>
                                No live jobs available right now
                            </strong>

                            <span>
                                JobScout understood your request,
                                but no live opportunities were returned.
                            </span>

                        </div>

                    </div>
                `;

                status.textContent =
                    "AI understood your request, but no live jobs are currently available.";

                status.className =
                    "agent-status warning";

                planBox.classList.add("warning");

            }


            planBox.innerHTML = html;

            planBox.classList.add("visible");

        }

        catch (error) {

            console.error("JobScout AI:", error);

            status.textContent =
                error.message ||
                "The AI job search is temporarily unavailable.";

            status.className =
                "agent-status error";

            planBox.innerHTML = `
                <div class="agent-error-card">

                    <div class="agent-error-icon">
                        ⚠️
                    </div>

                    <div>
                        <strong>
                            Search temporarily unavailable
                        </strong>

                        <p>
                            Please try again in a moment.
                        </p>
                    </div>

                </div>
            `;

            planBox.classList.add(
                "visible",
                "error"
            );

        }

        finally {

            button.disabled = false;

            button.innerHTML = `
                <span class="agent-button-icon">
                    ✦
                </span>

                <span>
                    Ask JobScout AI
                </span>

                <span class="agent-button-arrow">
                    →
                </span>
            `;

        }

    });


    function escapeHTML(value) {

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");

    }

});