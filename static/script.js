const jobForm = document.getElementById("jobForm");

const searchButton = document.getElementById("searchButton");

const loading = document.getElementById("loading");

const resultsSection = document.getElementById("resultsSection");

const jobsContainer = document.getElementById("jobsContainer");

const jobCount = document.getElementById("jobCount");


jobForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const role =
        document.getElementById("role").value.trim();

    const location =
        document.getElementById("location").value.trim();

    const experience =
        document.getElementById("experience").value;

    const skills =
        document.getElementById("skills").value.trim();


    if (!role || !location) {

        alert("Please enter a job role and location.");

        return;
    }


    // Show loading state

    loading.classList.remove("hidden");

    resultsSection.classList.add("hidden");

    jobsContainer.innerHTML = "";

    searchButton.disabled = true;

    searchButton.textContent =
        "🔎 JobScout AI is researching...";


    try {

        const response = await fetch(
            "/api/jobs",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    role: role,

                    location: location,

                    experience: experience,

                    skills: skills

                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.error || "Something went wrong."
            );
        }


        displayJobs(
            data.jobs || [],
            data.user_skills || []
        );


    } catch (error) {

        resultsSection.classList.remove("hidden");

        jobCount.textContent = "";

        jobsContainer.innerHTML = `

            <div class="error-card">

                <h3>⚠️ Search failed</h3>

                <p>
                    ${escapeHtml(error.message)}
                </p>

            </div>

        `;

    } finally {

        loading.classList.add("hidden");

        searchButton.disabled = false;

        searchButton.textContent =
            "🔍 Search Jobs";

    }

});


function displayJobs(jobs, userSkills) {

    resultsSection.classList.remove("hidden");


    jobCount.textContent =
        `${jobs.length} jobs analyzed`;


    if (!jobs.length) {

        jobsContainer.innerHTML = `

            <div class="job-card empty-card">

                <h3>No matching jobs found</h3>

                <p>
                    Try another role or location.
                </p>

            </div>

        `;

        return;
    }


    jobsContainer.innerHTML = jobs.map(
        (job, index) => {

            const title =
                job.title ||
                "Job Opportunity";


            const company =
                job.company ||
                "Company not specified";


            const location =
                job.location ||
                "Location not specified";


            const description =
                job.description ||
                "No description available.";


            const score =
                Number(job.match_score || 0);


            const matchedSkills =
                job.matched_skills || [];


            const missingSkills =
                job.missing_skills || [];


            const detectedSkills =
                job.detected_skills || [];


            const explanation =
                job.match_explanation ||
                "Review the job description carefully.";


            const applyLink =
                job.apply_link || "";


            const safeDescription =
                description.length > 650
                    ? description.substring(0, 650) + "..."
                    : description;


            const matchedHtml =
                matchedSkills.length
                    ? matchedSkills.map(
                        skill =>
                            `<span class="skill matched">
                                ✓ ${escapeHtml(skill)}
                             </span>`
                    ).join("")
                    : `<span class="no-skill">
                            No direct matches detected
                       </span>`;


            const missingHtml =
                missingSkills.length
                    ? missingSkills.map(
                        skill =>
                            `<span class="skill missing">
                                + ${escapeHtml(skill)}
                             </span>`
                    ).join("")
                    : `<span class="skill matched">
                            No major missing skills detected
                       </span>`;


            const detectedHtml =
                detectedSkills.length
                    ? detectedSkills.map(
                        skill =>
                            `<span class="skill detected">
                                ${escapeHtml(skill)}
                             </span>`
                    ).join("")
                    : `<span class="no-skill">
                            No technical skills detected
                       </span>`;


            const applyHtml =
                applyLink
                    ? `
                        <a
                            class="apply-button"
                            href="${escapeHtml(applyLink)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            View & Apply ↗
                        </a>
                    `
                    : `
                        <span class="no-link">
                            Application link unavailable
                        </span>
                    `;


            return `

                <article class="job-card">

                    <div class="job-top">

                        <div>

                            <span class="job-number">
                                #${index + 1}
                            </span>

                            <h3>
                                ${escapeHtml(title)}
                            </h3>

                            <div class="company">
                                ${escapeHtml(company)}
                            </div>

                        </div>


                        <div class="match-score">

                            <span class="score-number">
                                ${score}%
                            </span>

                            <span>
                                match
                            </span>

                        </div>

                    </div>


                    <div class="location">

                        📍 ${escapeHtml(location)}

                    </div>


                    <div class="match-message">

                        🧠 ${escapeHtml(explanation)}

                    </div>


                    <div class="skill-section">

                        <h4>
                            Your matching skills
                        </h4>

                        <div class="skills">

                            ${matchedHtml}

                        </div>

                    </div>


                    <div class="skill-section">

                        <h4>
                            Skills to review
                        </h4>

                        <div class="skills">

                            ${missingHtml}

                        </div>

                    </div>


                    <details class="details">

                        <summary>
                            View detected job skills
                        </summary>

                        <div class="skills detected-list">

                            ${detectedHtml}

                        </div>

                    </details>


                    <div class="description">

                        ${escapeHtml(safeDescription)}

                    </div>

                  <div class="job-verification">

    <div class="verification-title">
        🔎 Live Job Verification
    </div>

    <div class="verification-text">
        Found through
        <strong>
            ${escapeHtml(
                job.source ||
                "Google Jobs via SerpApi"
            )}
        </strong>
        .
        Verify the employer, vacancy status, and application details
        before submitting personal information.
    </div>

</div>


<div class="job-actions">

    ${applyHtml}

</div>

                </article>

            `;

        }
    ).join("");
}


function escapeHtml(value) {

    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");
}