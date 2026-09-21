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
                        🤖
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

            if (data.search_plan) {

                const plan = data.search_plan;

                const planSkills =
                    Array.isArray(plan.skills)
                        ? plan.skills
                        : [];

                const keywords =
                    Array.isArray(plan.search_keywords)
                        ? plan.search_keywords
                        : [];

                html += `
                    <div class="analysis-section search-strategy">

                        <div class="analysis-section-title">
                            🔎 AI Search Strategy
                        </div>

                        <div class="strategy-grid">

                            <div class="strategy-item">
                                <span class="strategy-label">
                                    🎯 Role
                                </span>

                                <strong>
                                    ${escapeHTML(
                                        plan.job_role ||
                                        "Not specified"
                                    )}
                                </strong>
                            </div>

                            <div class="strategy-item">
                                <span class="strategy-label">
                                    📍 Location
                                </span>

                                <strong>
                                    ${escapeHTML(
                                        plan.location ||
                                        "Not specified"
                                    )}
                                </strong>
                            </div>

                            <div class="strategy-item">
                                <span class="strategy-label">
                                    👨‍💻 Experience
                                </span>

                                <strong>
                                    ${escapeHTML(
                                        plan.experience_level ||
                                        "Not specified"
                                    )}
                                </strong>
                            </div>

                        </div>

                        ${
                            planSkills.length
                                ? `
                                    <div class="strategy-detail">

                                        <span class="strategy-label">
                                            🛠 Skills considered
                                        </span>

                                        <div class="strategy-tags">

                                            ${planSkills.map(
                                                skill =>
                                                    `
                                                    <span>
                                                        ${escapeHTML(skill)}
                                                    </span>
                                                    `
                                            ).join("")}

                                        </div>

                                    </div>
                                `
                                : ""
                        }

                        ${
                            keywords.length
                                ? `
                                    <div class="strategy-detail">

                                        <span class="strategy-label">
                                            🔍 Search keywords
                                        </span>

                                        <div class="strategy-tags keyword-tags">

                                            ${keywords.map(
                                                keyword =>
                                                    `
                                                    <span>
                                                        ${escapeHTML(keyword)}
                                                    </span>
                                                    `
                                            ).join("")}

                                        </div>

                                    </div>
                                `
                                : ""
                        }

                        ${
                            plan.search_strategy
                                ? `
                                    <div class="strategy-reason">

                                        <span class="strategy-label">
                                            💡 Strategy
                                        </span>

                                        <p>
                                            ${escapeHTML(
                                                plan.search_strategy
                                            )}
                                        </p>

                                    </div>
                                `
                                : ""
                        }

                    </div>
                `;
            }

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

                /*
                 * Send the AI-discovered jobs to the existing
                 * JobScout job-results renderer.
                 */
                renderAgentJobs(data.jobs || []);

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

                renderAgentJobs([]);
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


    /*
     * Render the jobs returned specifically by the AI Agent.
     *
     * This function tries to use the existing JobScout rendering
     * function from script.js instead of creating a second,
     * different job-card design.
     */
    function renderAgentJobs(jobs) {

        if (!Array.isArray(jobs)) {
            jobs = [];
        }

        /*
         * If script.js exposes a reusable renderer, use it.
         */
        if (typeof window.renderJobs === "function") {
            window.renderJobs(jobs);
            return;
        }

        if (typeof window.displayJobs === "function") {
            window.displayJobs(jobs);
            return;
        }

        if (typeof window.renderJobResults === "function") {
            window.renderJobResults(jobs);
            return;
        }

        /*
         * Fallback:
         * locate the existing job-results container and render
         * simple cards if no global renderer exists.
         */
        const resultsContainer =
            document.getElementById("jobResults") ||
            document.getElementById("jobsResults") ||
            document.querySelector(".jobs-grid") ||
            document.querySelector(".job-results");

        if (!resultsContainer) {
            console.warn(
                "JobScout AI: Could not find the existing job results container."
            );
            return;
        }

        if (jobs.length === 0) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <h3>No matching jobs found</h3>
                    <p>
                        Try another role, skill, or location.
                    </p>
                </div>
            `;
            return;
        }

        resultsContainer.innerHTML = jobs.map(function (job) {

            const title =
                job.title ||
                job.job_title ||
                "Job Opportunity";

            const company =
                job.company_name ||
                job.company ||
                "Company not specified";

            const location =
                job.location ||
                "Location not specified";

            const description =
                job.description ||
                "No job description available.";

            const applyLink =
                getApplyLink(job);

            return `
                <article class="job-card">

                    <div class="job-card-header">

                        <div>
                            <h3>
                                ${escapeHTML(title)}
                            </h3>

                            <p class="job-company">
                                ${escapeHTML(company)}
                            </p>

                            <p class="job-location">
                                📍 ${escapeHTML(location)}
                            </p>
                        </div>

                    </div>

                    <div class="job-description">
                        ${escapeHTML(description)}
                    </div>

                    <div class="job-card-footer">

                        ${
                            applyLink
                            ? `
                                <a
                                    class="apply-button"
                                    href="${escapeAttribute(applyLink)}"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    View & Apply →
                                </a>
                            `
                            : `
                                <span class="apply-unavailable">
                                    Application link unavailable
                                </span>
                            `
                        }

                    </div>

                </article>
            `;

        }).join("");
    }


    function getApplyLink(job) {

        if (
            Array.isArray(job.apply_options) &&
            job.apply_options.length > 0
        ) {

            for (const option of job.apply_options) {

                if (option && option.link) {
                    return option.link;
                }

            }
        }

        return (
            job.share_link ||
            job.link ||
            job.url ||
            ""
        );
    }


    function escapeHTML(value) {

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    function escapeAttribute(value) {

        return escapeHTML(value);
    }

});