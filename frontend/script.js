"use strict";

const API_BASE_URL =
    location.port === "5500" || location.protocol === "file:"
        ? "http://127.0.0.1:5000"
        : "";

// ==================================================
// DOM ELEMENTS
// ==================================================

const studentForm = document.getElementById("student-form");
const analyzeButton = document.getElementById("analyze-button");
const formMessage = document.getElementById("form-message");
const resultsSection = document.getElementById("results");
const resultsContent = document.getElementById("results-content");

const educationStage = document.getElementById("education-stage");
const schoolFields = document.getElementById("school-fields");
const collegeFields = document.getElementById("college-fields");

const schoolBoard = document.getElementById("school-board");
const schoolClass = document.getElementById("school-class");
const schoolStream = document.getElementById("school-stream");
const schoolSubjects = document.getElementById("school-subjects");
const schoolGoal = document.getElementById("school-goal");

const degree = document.getElementById("degree");
const department = document.getElementById("department");
const studyYear = document.getElementById("study-year");
const careerGoal = document.getElementById("career-goal");

// ==================================================
// GENERAL HELPERS
// ==================================================

function getElementValue(id, fallback = "") {
    const element = document.getElementById(id);
    return element ? element.value.trim() : fallback;
}

function showMessage(message, type = "") {
    if (!formMessage) {
        console.log(message);
        return;
    }

    formMessage.textContent = message;
    formMessage.className = "form-message";

    if (type) {
        formMessage.classList.add(type);
    }
}

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[character];
    });
}

function formatNumber(value, decimalPlaces = 1) {
    if (value === null || value === undefined || value === "") {
        return "N/A";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "N/A";
    }

    return number.toFixed(decimalPlaces).replace(/\.0$/, "");
}

function formatHours(value) {
    return `${formatNumber(value)} ${Number(value) === 1 ? "hour" : "hours"}`;
}

function getField(object, keys, fallback = "N/A") {
    if (!object || typeof object !== "object") {
        return fallback;
    }

    for (const key of keys) {
        const value = object[key];

        if (value !== undefined && value !== null && value !== "") {
            return value;
        }
    }

    return fallback;
}

function getArray(object, keys) {
    const value = getField(object, keys, []);
    return Array.isArray(value) ? value : [];
}

function normalizeArray(value) {
    if (Array.isArray(value)) {
        return value;
    }

    if (typeof value === "string" && value.trim()) {
        return value.split(",").map(item => item.trim()).filter(Boolean);
    }

    return [];
}

function displayItemName(item, keys = ["name", "title", "skill"]) {
    if (typeof item === "string" || typeof item === "number") {
        return String(item);
    }

    return String(getField(item, keys, "Not specified"));
}

function renderList(items, renderer) {
    if (!Array.isArray(items) || items.length === 0) {
        return "<li>No data available.</li>";
    }

    return items.map((item, index) => renderer(item, index)).join("");
}

function getSafeURL(value) {
    if (typeof value !== "string" || !value.trim()) {
        return "";
    }

    try {
        const parsed = new URL(value);

        if (parsed.protocol === "https:" || parsed.protocol === "http:") {
            return parsed.href;
        }
    } catch {
        return "";
    }

    return "";
}

function parseSkills(value) {
    if (!value || !value.trim()) {
        return [];
    }

    return value
        .split(",")
        .map(item => item.trim())
        .filter(Boolean)
        .map(item => {
            const separator = item.lastIndexOf(":");

            if (separator === -1) {
                return {
                    skill: item,
                    level: "Beginner"
                };
            }

            return {
                skill: item.slice(0, separator).trim(),
                level: item.slice(separator + 1).trim() || "Beginner"
            };
        })
        .filter(item => item.skill);
}

// ==================================================
// EDUCATION FORM SWITCHING
// ==================================================

function setGroupVisibility(group, visible) {
    if (!group) {
        return;
    }

    group.classList.toggle("hidden", !visible);

    group.querySelectorAll("input, select, textarea").forEach(field => {
        field.disabled = !visible;
    });
}

// ==================================================
// STAGE-SPECIFIC LABELS (Graduate / Working Professional)
// Only the visible text changes. Field IDs and option values stay
// the same, so the backend request is not affected.
// ==================================================

const STUDY_YEAR_TEXT = {
    College: {
        label: "Current Study Year",
        options: {
            "1": "Year 1",
            "2": "Year 2",
            "3": "Year 3",
            "4": "Year 4",
            "5": "Year 5 or above"
        }
    },
    Graduate: {
        label: "Years Since Graduation",
        options: {
            "1": "Just graduated",
            "2": "1 year",
            "3": "2 years",
            "4": "3 years",
            "5": "4 years or more"
        }
    },
    "Working Professional": {
        label: "Work Experience",
        options: {
            "1": "Fresher (0 to 1 year)",
            "2": "1 to 2 years",
            "3": "2 to 3 years",
            "4": "3 to 5 years",
            "5": "5 years or more"
        }
    }
};

function applyStageLabels(stage) {
    const text = STUDY_YEAR_TEXT[stage] || STUDY_YEAR_TEXT.College;
    const label = document.querySelector('label[for="study-year"]');

    if (label) {
        label.textContent = text.label;
    }

    if (!studyYear) {
        return;
    }

    Array.from(studyYear.options).forEach(option => {
        if (text.options[option.value]) {
            option.textContent = text.options[option.value];
        }
    });
}

function updateEducationFields() {
    if (!educationStage) {
        return;
    }

    const isSchool = educationStage.value === "School";

    applyStageLabels(educationStage.value);
    setGroupVisibility(schoolFields, isSchool);
    setGroupVisibility(collegeFields, !isSchool);

    [schoolBoard, schoolClass, schoolGoal].forEach(field => {
        if (field) {
            field.required = isSchool;
        }
    });

    [degree, department, studyYear, careerGoal].forEach(field => {
        if (field) {
            field.required = !isSchool;
        }
    });

    if (analyzeButton) {
        analyzeButton.textContent = isSchool
            ? "Create My Learning Roadmap →"
            : "Analyze My Profile →";
    }
}

if (educationStage) {
    educationStage.addEventListener("change", updateEducationFields);
    updateEducationFields();
}

// ==================================================
// COLLEGE: PROFILE OVERVIEW
// ==================================================

// ==================================================
// CHART HELPERS (pure HTML, CSS and SVG, no libraries)
// ==================================================

function clampPercent(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return 0;
    }

    return Math.min(100, Math.max(0, number));
}

// Circular progress ring. A missing value is drawn as an empty ring.
function renderRing(value, label) {
    const hasValue = value !== null &&
        value !== undefined &&
        Number.isFinite(Number(value));

    const percent = hasValue ? clampPercent(value) : 0;
    const text = hasValue ? `${formatNumber(percent)}%` : "N/A";

    return `
        <div class="ring" role="img"
             aria-label="${escapeHTML(label)}: ${escapeHTML(text)}">
            <svg viewBox="0 0 120 120" aria-hidden="true">
                <circle class="ring-track" cx="60" cy="60" r="52"
                        pathLength="100"></circle>
                <circle class="ring-value" cx="60" cy="60" r="52"
                        pathLength="100" style="--value:${percent}"></circle>
            </svg>
            <span class="ring-number">${escapeHTML(text)}</span>
        </div>
    `;
}

// Thin progress bar without a label (used inside list items).
function renderMeter(percent, tone = "accent") {
    return `
        <div class="bar-track" aria-hidden="true">
            <div class="bar-fill tone-${tone}"
                 style="--value:${clampPercent(percent)}%"></div>
        </div>
    `;
}

// One labelled bar: label on the left, value on the right.
function renderBarRow(label, value, max, display, tone = "accent") {
    const percent = max > 0 ? (value / max) * 100 : 0;

    return `
        <div class="bar-row">
            <div class="bar-label">
                <span>${escapeHTML(label)}</span>
                <strong>${escapeHTML(display)}</strong>
            </div>
            ${renderMeter(percent, tone)}
        </div>
    `;
}

// One bar split into coloured parts, with a legend underneath.
// segments: [{ label, value, display, tone }]
function renderStackedBar(segments) {
    const visible = segments.filter(segment => segment.value > 0);
    const total = visible.reduce((sum, segment) => sum + segment.value, 0);

    if (!total) {
        return "";
    }

    return `
        <div class="stack-bar" role="img" aria-label="${escapeHTML(
            visible.map(segment =>
                `${segment.label}: ${segment.display}`
            ).join(", ")
        )}">
            ${visible.map(segment => `
                <div class="stack-seg tone-${segment.tone}"
                     style="--value:${(segment.value / total) * 100}%"></div>
            `).join("")}
        </div>

        <ul class="chart-legend">
            ${visible.map(segment => `
                <li>
                    <i class="legend-dot tone-${segment.tone}"></i>
                    ${escapeHTML(segment.label)}
                    <strong>${escapeHTML(segment.display)}</strong>
                </li>
            `).join("")}
        </ul>
    `;
}

function levelTone(level) {
    const text = String(level || "").toLowerCase();

    if (text.includes("begin")) {
        return "light";
    }

    if (text.includes("inter")) {
        return "mid";
    }

    return "accent";
}

function shortHours(value) {
    return `${formatNumber(value)} h`;
}

// Starts the bar, ring and segment animations after the HTML is in place.
function animateCharts() {
    if (!resultsContent) {
        return;
    }

    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            resultsContent
                .querySelectorAll(".bar-fill, .ring-value, .stack-seg")
                .forEach(element => element.classList.add("is-ready"));
        });
    });
}

function renderOverview(data) {
    const profile = data.profile_analysis || {};
    const summary = profile.summary || {};
    const gap = data.skill_gap_analysis || {};
    const roadmap = data.learning_roadmap || {};

    const readiness = getField(profile, ["readiness_score"], null);

    const coverage = getField(
        gap,
        ["skill_coverage_percentage", "skill_coverage", "coverage_percentage", "coverage"],
        null
    );

    const hours = getField(
        roadmap,
        ["total_learning_hours", "total_estimated_hours", "total_hours", "estimated_hours"],
        null
    );

    return `
        <div class="result-overview">
            <article class="result-stat has-ring">
                              <p>Profile Completeness</p>
                ${renderRing(readiness, "Profile Readiness")}
            </article>
            <article class="result-stat has-ring">
                <p>Skill Coverage</p>
                ${renderRing(coverage, "Skill Coverage")}
            </article>

            <article class="result-stat">
                <p>Learning Hours</p>
                <h3>${hours !== null
                    ? escapeHTML(formatNumber(hours))
                    : "N/A"}</h3>
            </article>
        </div>

        <div class="result-panel">
            <h3>Profile Summary</h3>
            <ul class="result-list">
                <li><strong>Department:</strong>
                    ${escapeHTML(getField(summary, ["department"]))}
                </li>
                <li><strong>Career Goal:</strong>
                    ${escapeHTML(
                        data.selected_career ||
                        getField(summary, ["career_goal"])
                    )}
                </li>
                <li><strong>Weekly Study Time:</strong>
                    ${escapeHTML(formatHours(
                        getField(summary, ["weekly_learning_hours"], 0)
                    ))}
                </li>
                <li><strong>Learning Style:</strong>
                    ${escapeHTML(getField(summary, ["learning_style"]))}
                </li>
            </ul>
        </div>
    `;
}

// ==================================================
// COLLEGE: CAREER PREDICTIONS
// ==================================================

function renderTargetCareerMatch(predictionData, predictions) {
    const target = predictionData.target_career_match;
    const topScore = Number(predictions[0] && predictions[0].match_percent);
    let html = "";

    if (target) {
        html += `
            <p><strong>Your target career:</strong>
                ${escapeHTML(target.career_name)} - rank
                ${escapeHTML(String(target.rank))} of
                ${escapeHTML(String(target.total_careers))}
                (${escapeHTML(formatNumber(target.match_percent))}% match)
            </p>
        `;
    }

    if (Number.isFinite(topScore) && topScore < 15) {
        html += `
            <p>Match scores are low. Add more skills and interests
            to get sharper career predictions.</p>
        `;
    }

    return html;
}

function renderCareerPredictions(data) {
    const predictionData = data.career_predictions || {};

    const predictions = getArray(predictionData, [
        "recommendations",
        "predictions",
        "careers"
    ]);

    if (!predictions.length) {
        return `
            <div class="result-panel">
                <h3>AI Career Predictions</h3>
                <p>No career predictions were returned by the backend.</p>
            </div>
        `;
    }

    return `
        <div class="result-panel">
            <h3>AI Career Predictions</h3>

            <ul class="result-list">
                ${renderList(predictions, (career, index) => {
                    const name = displayItemName(career, [
                        "career_name",
                        "name",
                        "career"
                    ]);

                    const score = getField(career, [
                        "prediction_score",
                        "similarity_score",
                        "score"
                    ], null);

                    const departmentName = getField(
                        career,
                        ["department"],
                        null
                    );

                    let scoreHTML = "";

                    if (score !== null) {
                        const numericScore = Number(score);

                        if (Number.isFinite(numericScore)) {
                            const percentage = numericScore <= 1
                                ? numericScore * 100
                                : numericScore;

                            scoreHTML = `
                                <p>Match score:
                                    ${escapeHTML(formatNumber(percentage))}%
                                </p>
                            `;
                        }
                    }

                    return `
                        <li>
                            <strong>${index + 1}. ${escapeHTML(name)}</strong>
                            ${departmentName !== null
                                ? `<p>Department: ${
                                    escapeHTML(departmentName)
                                }</p>`
                                : ""}
                            ${scoreHTML}
                        </li>
                    `;
                })}
            </ul>

            ${renderTargetCareerMatch(predictionData, predictions)}
            <p>Match scores are estimates, not guaranteed probabilities.</p>
        </div>
    `;
}
// ==================================================
// COLLEGE: SKILL GAP ANALYSIS
// ==================================================

function renderSkillGaps(data) {
    const gap = data.skill_gap_analysis || {};

    const matchedSkills = getArray(gap, [
        "matched_skills",
        "known_skills"
    ]);

    const missingSkills = getArray(gap, [
        "missing_skills",
        "skill_gaps"
    ]);

    const requiredCount = getField(gap, [
        "required_skill_count",
        "total_required_skills"
    ], null);

    function skillTags(skills, emptyMessage) {
        if (!skills.length) {
            return escapeHTML(emptyMessage);
        }

        return skills.map(skill => `
            <span class="result-tag">
                ${escapeHTML(displayItemName(skill, ["skill", "name"]))}
            </span>
        `).join(" ");
    }

    return `
        <div class="result-panel">
            <h3>Skill Gap Analysis</h3>

            ${requiredCount !== null
                ? `<p>Required skills: ${
                    escapeHTML(requiredCount)
                }</p>`
                : ""}

            ${renderStackedBar([
                {
                    label: "Known",
                    value: matchedSkills.length,
                    display: String(matchedSkills.length),
                    tone: "accent"
                },
                {
                    label: "To develop",
                    value: missingSkills.length,
                    display: String(missingSkills.length),
                    tone: "warm"
                }
            ])}

            <h4>Skills You Already Have</h4>
            <p>${skillTags(
                matchedSkills,
                "No matching skills were identified."
            )}</p>

            <h4 style="margin-top: 18px;">Skills to Develop</h4>
            <p>${skillTags(
                missingSkills,
                "No missing skills were reported."
            )}</p>
        </div>
    `;
}

// ==================================================
// COLLEGE: LEARNING ROADMAP
// ==================================================

function renderRoadmapChart(steps) {
    const rows = steps
        .filter(step => step && typeof step === "object")
        .map(step => ({
            name: displayItemName(step, [
                "skill",
                "skill_name",
                "name",
                "title"
            ]),
            hours: Number(getField(step, [
                "estimated_hours",
                "duration_hours",
                "hours"
            ], 0)) || 0,
            level: getField(step, ["level", "difficulty"], "")
        }))
        .filter(row => row.hours > 0);

    if (!rows.length) {
        return "";
    }

    const maxHours = Math.max(...rows.map(row => row.hours));

    return `
        <div class="chart-block">
            <h4>Time per Skill</h4>

            ${rows.map(row => renderBarRow(
                row.name,
                row.hours,
                maxHours,
                shortHours(row.hours),
                levelTone(row.level)
            )).join("")}

            <ul class="chart-legend">
                <li><i class="legend-dot tone-light"></i>Beginner</li>
                <li><i class="legend-dot tone-mid"></i>Intermediate</li>
                <li><i class="legend-dot tone-accent"></i>Advanced</li>
            </ul>
        </div>
    `;
}

function renderRoadmap(data) {
    const roadmapData = data.learning_roadmap || {};

    const roadmap = getArray(roadmapData, [
        "roadmap",
        "steps",
        "learning_steps"
    ]);

    if (!roadmap.length) {
        return `
            <div class="result-panel">
                <h3>Your Learning Roadmap</h3>
                <p>No roadmap steps were returned by the backend.</p>
            </div>
        `;
    }

    return `
        <div class="result-panel">
            <h3>Your Learning Roadmap</h3>
            <p>Follow these learning steps in the recommended order.</p>

            ${renderRoadmapChart(roadmap)}

            <ol class="result-list">
                ${renderList(roadmap, (step, index) => {
                    const skill = displayItemName(step, [
                        "skill",
                        "skill_name",
                        "name",
                        "title"
                    ]);

                    const duration = typeof step === "object"
                        ? getField(step, [
                            "estimated_hours",
                            "duration_hours",
                            "hours"
                        ], null)
                        : null;

                    const level = typeof step === "object"
                        ? getField(step, ["level", "difficulty"], null)
                        : null;

                    const prerequisites = typeof step === "object"
                        ? normalizeArray(step.prerequisites)
                        : [];

                    return `
                        <li>
                            <strong>${index + 1}. ${escapeHTML(skill)}</strong>

                            ${duration !== null
                                ? `<p>Estimated time: ${
                                    escapeHTML(formatHours(duration))
                                }</p>`
                                : ""}

                            ${level !== null
                                ? `<p>Level: ${escapeHTML(level)}</p>`
                                : ""}

                            ${prerequisites.length
                                ? `<p>Prerequisites: ${
                                    escapeHTML(prerequisites.join(", "))
                                }</p>`
                                : ""}
                        </li>
                    `;
                })}
            </ol>

            ${getField(
                roadmapData,
                ["total_learning_hours", "total_estimated_hours", "total_hours"],
                null
            ) !== null
                ? `<p><strong>Total hours:</strong> ${
                    escapeHTML(getField(
                        roadmapData,
                        ["total_learning_hours", "total_estimated_hours", "total_hours"],
                        0
                    ))
                }</p>`
                : ""}
        </div>
    `;
}

// ==================================================
// SHARED: LEARNING RESOURCES
// ==================================================

function collectResources(resourceData) {
    if (Array.isArray(resourceData)) {
        return resourceData;
    }

    if (!resourceData || typeof resourceData !== "object") {
        return [];
    }

    if (Array.isArray(resourceData.recommendations)) {
        const resources = [];

        resourceData.recommendations.forEach(group => {
            if (Array.isArray(group.resources)) {
                group.resources.forEach(resource => {
                    resources.push({
                        ...resource,
                        skill: resource.skill ||
                            resource.skill_name ||
                            group.skill ||
                            group.subject ||
                            ""
                    });
                });
            } else {
                resources.push(group);
            }
        });

        return resources;
    }

    return getArray(resourceData, [
        "resources",
        "recommended_resources"
    ]);
}

function renderResourceList(resources, schoolMode = false) {
    if (!resources.length) {
        return `<p>No matching resources were returned by the backend.</p>`;
    }

    return `
        <ul class="result-list">
            ${renderList(resources, (resource, index) => {
                const title = displayItemName(resource, [
                    "title",
                    "name",
                    "resource_name"
                ]);

                const subject = getField(resource, [
                    "subject",
                    "skill",
                    "skill_name",
                    "topic"
                ], "");

                const type = getField(resource, [
                    "type",
                    "resource_type"
                ], "Learning Resource");

                const platform = getField(resource, ["platform"], "");
                const level = getField(resource, ["level"], "");

                const url = typeof resource === "object"
                    ? getSafeURL(getField(resource, ["url", "link"], ""))
                    : "";

                return `
                    <li class="resource-item">
                        <strong>${escapeHTML(title)}</strong>

                        ${subject
                            ? `<p><strong>${
                                schoolMode ? "Subject" : "Skill"
                            }:</strong> ${escapeHTML(subject)}</p>`
                            : ""}

                        <p><strong>Type:</strong> ${escapeHTML(type)}</p>

                        ${platform
                            ? `<p><strong>Platform:</strong> ${
                                escapeHTML(platform)
                            }</p>`
                            : ""}

                        ${level
                            ? `<p><strong>Level:</strong> ${
                                escapeHTML(level)
                            }</p>`
                            : ""}

                        ${url
                            ? `<p><a href="${escapeHTML(url)}"
                                   target="_blank"
                                   rel="noopener noreferrer">
                                   Open Learning Resource ↗
                               </a></p>`
                            : "<p>Link unavailable.</p>"}
                    </li>
                `;
            })}
        </ul>
    `;
}

function renderResources(data) {
    const resources = collectResources(
        data.resource_recommendations || {}
    );

    return `
        <div class="result-panel">
            <h3>Recommended Learning Resources</h3>
            ${renderResourceList(resources)}
        </div>
    `;
}

// ==================================================
// COLLEGE: STUDY PLAN
// ==================================================

// ==================================================
// COLLEGE: WEEKLY STUDY PLAN HELPERS
// ==================================================

const WEEKS_VISIBLE_BY_DEFAULT = 6;

function formatShortDate(value) {
    const parsed = new Date(`${value}T00:00:00`);

    if (Number.isNaN(parsed.getTime())) {
        return String(value);
    }

    return parsed.toLocaleDateString("en-GB", {
        day: "numeric",
        month: "short"
    });
}

// Groups daily sessions into weeks, using the backend "week" number.
// If a session has no week number, every 7 sessions form one week.
function groupSessionsByWeek(sessions) {
    const weeks = new Map();

    sessions.forEach((session, index) => {
        if (!session || typeof session !== "object") {
            return;
        }

        const weekNumber = Number(
            getField(session, ["week", "week_number"], Math.floor(index / 7) + 1)
        );

        if (!weeks.has(weekNumber)) {
            weeks.set(weekNumber, {
                week: weekNumber,
                start: null,
                end: null,
                hours: 0,
                skills: []
            });
        }

        const entry = weeks.get(weekNumber);
        const date = getField(session, ["date", "study_date"], null);
        const hours = Number(getField(session, [
            "study_hours",
            "hours",
            "duration_hours",
            "estimated_hours"
        ], 0));
        const skill = displayItemName(session, [
            "skill",
            "skill_name",
            "topic",
            "title"
        ]);

        if (date !== null) {
            entry.start = entry.start === null || date < entry.start
                ? date
                : entry.start;
            entry.end = entry.end === null || date > entry.end
                ? date
                : entry.end;
        }

        entry.hours += Number.isFinite(hours) ? hours : 0;

        if (skill && !entry.skills.includes(skill)) {
            entry.skills.push(skill);
        }
    });

    return Array.from(weeks.values()).sort((a, b) => a.week - b.week);
}

function renderWeekCard(week) {
    const dateRange = week.start !== null
        ? week.start === week.end
            ? formatShortDate(week.start)
            : `${formatShortDate(week.start)} – ${formatShortDate(week.end)}`
        : "";

    return `
        <article class="week-card">
            <div class="week-card-head">
                <span class="week-number">Week ${escapeHTML(week.week)}</span>
                <span class="week-hours">${
                    escapeHTML(formatNumber(week.hours))
                } hrs</span>
            </div>

            ${dateRange
                ? `<p class="week-dates">${escapeHTML(dateRange)}</p>`
                : ""}

            <div class="week-skills">
                ${week.skills.map(skill =>
                    `<span class="result-tag">${escapeHTML(skill)}</span>`
                ).join("")}
            </div>
        </article>
    `;
}

function renderWeeklyPlan(sessions) {
    const weeks = groupSessionsByWeek(sessions);

    if (!weeks.length) {
        return "<p>No study sessions were returned by the backend.</p>";
    }

    const visibleWeeks = weeks.slice(0, WEEKS_VISIBLE_BY_DEFAULT);
    const hiddenWeeks = weeks.slice(WEEKS_VISIBLE_BY_DEFAULT);

    return `
        <h4>Weekly Plan</h4>

        <div class="week-grid">
            ${visibleWeeks.map(renderWeekCard).join("")}
        </div>

        ${hiddenWeeks.length
            ? `<details class="week-more">
                   <summary>Show remaining ${hiddenWeeks.length} weeks</summary>
                   <div class="week-grid">
                       ${hiddenWeeks.map(renderWeekCard).join("")}
                   </div>
               </details>`
            : ""}
    `;
}

function renderStudyPlan(data) {
    const plan = data.study_plan || {};

    const sessions = getArray(plan, [
        "study_plan",
        "sessions",
        "daily_sessions",
        "study_sessions",
        "plan"
    ]);

    const totalHours = getField(plan, [
        "total_planned_hours",
        "total_hours",
        "estimated_total_hours"
    ], null);

    const weeklyHours = getField(plan, [
        "weekly_learning_hours",
        "hours_per_week"
    ], null);

    const duration = getField(plan, [
        "estimated_duration_days",
        "duration_days",
        "total_days"
    ], null);

    return `
        <div class="result-panel">
            <h3>Your Study Plan</h3>

            <ul class="result-list">
                ${totalHours !== null
                    ? `<li><strong>Total planned hours:</strong> ${
                        escapeHTML(formatNumber(totalHours))
                    }</li>`
                    : ""}

                ${weeklyHours !== null
                    ? `<li><strong>Weekly study time:</strong> ${
                        escapeHTML(formatHours(weeklyHours))
                    }</li>`
                    : ""}

                ${duration !== null
                    ? `<li><strong>Estimated duration:</strong> ${
                        escapeHTML(duration)
                    } days</li>`
                    : ""}
            </ul>

            ${renderWeeklyPlan(sessions)}
        </div>
    `;
}

// ==================================================
// SCHOOL: DATA NORMALIZATION
// ==================================================

function getSchoolRoadmapItems(roadmapData) {
    if (Array.isArray(roadmapData)) {
        return roadmapData;
    }

    if (!roadmapData || typeof roadmapData !== "object") {
        return [];
    }

    return getArray(roadmapData, [
        "roadmap",
        "steps",
        "learning_steps",
        "topics",
        "items"
    ]);
}

function getSchoolStudySessions(studyPlanData) {
    if (Array.isArray(studyPlanData)) {
        return studyPlanData;
    }

    if (!studyPlanData || typeof studyPlanData !== "object") {
        return [];
    }

    return getArray(studyPlanData, [
        "study_plan",
        "sessions",
        "days",
        "plan",
        "daily_sessions",
        "study_sessions"
    ]);
}

// ==================================================
// SCHOOL: WEEKLY STUDY PLAN HELPERS
// ==================================================

// The backend sends a "week" number for every school session.
// If it is missing, topics are packed into weeks without exceeding
// the student's weekly study hours.
const SCHOOL_REVIEW_ACTIVITIES = [
    "Revision",
    "Final revision",
    "Mock test",
    "Practice"
];

const SCHOOL_HIDDEN_SUBJECTS = ["Weekly Revision", "Practice"];

function toSchoolTopic(session) {
    return {
        name: displayItemName(session, [
            "topic",
            "title",
            "name",
            "subject"
        ]),
        subject: String(getField(session, ["subject", "subject_name"], "")),
        activity: String(getField(session, ["activity"], "")),
        hours: Number(getField(session, [
            "hours",
            "estimated_hours",
            "duration_hours"
        ], 0)) || 0,
        notes: String(getField(session, ["notes"], ""))
    };
}

function groupSchoolSessionsByWeek(sessions, weeklyHours) {
    const validSessions = sessions.filter(
        session => session && typeof session === "object"
    );

    const hasWeekNumbers = validSessions.length > 0 && validSessions.every(
        session => Number.isFinite(Number(session.week))
    );

    const weeks = [];

    if (hasWeekNumbers) {
        const byWeek = new Map();

        validSessions.forEach(session => {
            const weekNumber = Number(session.week);

            if (!byWeek.has(weekNumber)) {
                byWeek.set(weekNumber, {
                    week: weekNumber,
                    hours: 0,
                    topics: []
                });
            }

            const entry = byWeek.get(weekNumber);
            const topic = toSchoolTopic(session);

            entry.hours += topic.hours;
            entry.topics.push(topic);
        });

        return Array.from(byWeek.values()).sort((a, b) => a.week - b.week);
    }

    const weekLimit = Number.isFinite(weeklyHours) && weeklyHours > 0
        ? weeklyHours
        : 7;

    let current = null;

    validSessions.forEach(session => {
        const topic = toSchoolTopic(session);

        if (
            !current ||
            (current.hours + topic.hours > weekLimit && current.topics.length)
        ) {
            current = {
                week: weeks.length + 1,
                hours: 0,
                topics: []
            };
            weeks.push(current);
        }

        current.hours += topic.hours;
        current.topics.push(topic);
    });

    return weeks;
}

function renderSchoolWeekCard(week) {
    return `
        <article class="week-card">
            <div class="week-card-head">
                <span class="week-number">Week ${escapeHTML(week.week)}</span>
                <span class="week-hours">${
                    escapeHTML(formatNumber(week.hours))
                } hrs</span>
            </div>

            <ul class="week-topics">
                ${week.topics.map(topic => {
                    const isReview = SCHOOL_REVIEW_ACTIVITIES.includes(
                        topic.activity
                    );

                    const details = [
                        SCHOOL_HIDDEN_SUBJECTS.includes(topic.subject)
                            ? ""
                            : topic.subject,
                        topic.activity,
                        topic.hours ? formatHours(topic.hours) : ""
                    ].filter(Boolean).join(" · ");

                    return `
                        <li${isReview ? ' class="is-review"' : ""}>
                            <span>${escapeHTML(topic.name)}</span>
                            ${details
                                ? `<small>${escapeHTML(details)}</small>`
                                : ""}
                            ${topic.notes
                                ? `<small class="week-note">${
                                    escapeHTML(topic.notes)
                                }</small>`
                                : ""}
                        </li>
                    `;
                }).join("")}
            </ul>
        </article>
    `;
}

function renderSchoolWeeklyPlan(sessions, weeklyHours) {
    const weeks = groupSchoolSessionsByWeek(sessions, weeklyHours);

    if (!weeks.length) {
        return "<p>No study sessions were returned by the backend.</p>";
    }

    const visibleWeeks = weeks.slice(0, WEEKS_VISIBLE_BY_DEFAULT);
    const hiddenWeeks = weeks.slice(WEEKS_VISIBLE_BY_DEFAULT);

    return `
        <div class="week-grid">
            ${visibleWeeks.map(renderSchoolWeekCard).join("")}
        </div>

        ${hiddenWeeks.length
            ? `<details class="week-more">
                   <summary>Show remaining ${hiddenWeeks.length} weeks</summary>
                   <div class="week-grid">
                       ${hiddenWeeks.map(renderSchoolWeekCard).join("")}
                   </div>
               </details>`
            : ""}
    `;
}

function getSchoolSubjects(profile, schoolAnalysis) {
    const source = profile.school_subjects ||
        schoolAnalysis.subjects ||
        schoolAnalysis.school_subjects ||
        [];

    if (Array.isArray(source)) {
        return source.map(subject => {
            if (typeof subject === "string") {
                return subject;
            }

            return displayItemName(subject, [
                "subject",
                "subject_name",
                "name",
                "title"
            ]);
        }).filter(Boolean);
    }

    return normalizeArray(source);
}

// ==================================================
// SCHOOL: LEARNING ROADMAP AND RESOURCES
// ==================================================

function renderSchoolSubjectChart(roadmapItems) {
    const totals = new Map();

    roadmapItems.forEach(item => {
        if (!item || typeof item !== "object") {
            return;
        }

        const subject = String(getField(item, ["subject"], "General"));
        const hours = Number(getField(item, [
            "estimated_hours",
            "hours"
        ], 0)) || 0;

        totals.set(subject, (totals.get(subject) || 0) + hours);
    });

    const rows = Array.from(totals.entries()).filter(([, hours]) => hours > 0);

    if (!rows.length) {
        return "";
    }

    const maxHours = Math.max(...rows.map(([, hours]) => hours));

    return `
        <div class="chart-block">
            <h4>Study Time by Subject</h4>
            ${rows.map(([subject, hours]) => renderBarRow(
                subject,
                hours,
                maxHours,
                shortHours(hours)
            )).join("")}
        </div>
    `;
}

function renderSchoolPlanBreakdown(sessions) {
    const hoursFor = activities => sessions
        .filter(session => session && activities.includes(session.activity))
        .reduce((sum, session) => sum + (Number(session.hours) || 0), 0);

    const newTopics = hoursFor(["Learn and practise", "Continue practice"]);
    const revision = hoursFor(["Revision", "Practice"]);
    const finalRevision = hoursFor(["Final revision"]);
    const mockTests = hoursFor(["Mock test"]);

    if (!(newTopics + revision + finalRevision + mockTests)) {
        return "";
    }

    return `
        <div class="chart-block">
            <h4>How Your Time Is Used</h4>
            ${renderStackedBar([
                {
                    label: "New topics",
                    value: newTopics,
                    display: shortHours(newTopics),
                    tone: "accent"
                },
                {
                    label: "Revision and practice",
                    value: revision,
                    display: shortHours(revision),
                    tone: "mid"
                },
                {
                    label: "Final revision",
                    value: finalRevision,
                    display: shortHours(finalRevision),
                    tone: "warm"
                },
                {
                    label: "Mock tests",
                    value: mockTests,
                    display: shortHours(mockTests),
                    tone: "ink"
                }
            ])}
        </div>
    `;
}

function renderSchoolResults(data, profile) {
    const schoolAnalysis = data.school_analysis &&
        typeof data.school_analysis === "object"
        ? data.school_analysis
        : {};

    // Backend may return either a roadmap object or a direct array.
    const roadmapData =
        data.school_roadmap ??
        data.school_learning_roadmap ??
        data.learning_roadmap ??
        schoolAnalysis.school_roadmap ??
        schoolAnalysis.learning_roadmap ??
        {};

    const roadmap = getSchoolRoadmapItems(roadmapData);

    const subjects = getSchoolSubjects(profile, schoolAnalysis);

    // Accept all school resource response formats.
    const resourceData =
        data.school_resources ??
        data.school_resource_recommendations ??
        data.resource_recommendations ??
        schoolAnalysis.school_resources ??
        schoolAnalysis.resources ??
        [];

    const resources = collectResources(resourceData);

    // Backend currently returns school_study_plan as an array.
    const studyPlanData =
        data.school_study_plan ??
        data.study_plan ??
        schoolAnalysis.school_study_plan ??
        schoolAnalysis.study_plan ??
        [];

    const sessions = getSchoolStudySessions(studyPlanData);

    const weeklyHours = Number(profile.weekly_learning_hours || 0);

    const totalHours = getField(
        roadmapData,
        ["total_learning_hours", "total_estimated_hours", "total_hours", "estimated_hours"],
        getField(
            schoolAnalysis,
            ["total_learning_hours", "total_estimated_hours", "total_hours"],
            null
        )
    );

    const roadmapHTML = roadmap.length
        ? `<ol class="result-list">
            ${renderList(roadmap, (step, index) => {
                let topic = displayItemName(step, [
                    "topic",
                    "title",
                    "skill",
                    "skill_name",
                    "subject",
                    "name"
                ]);

                // Avoid showing duplicate numbering if the topic already
                // begins with a number, for example "1. Electrostatics".
                topic = topic.replace(/^\s*\d+[\s.)-]+\s*/, "");

                const hours = typeof step === "object"
                    ? getField(step, [
                        "estimated_hours",
                        "duration_hours",
                        "hours"
                    ], null)
                    : null;

                const description = typeof step === "object"
                    ? getField(step, ["description"], "")
                    : "";

                const subject = typeof step === "object"
                    ? getField(step, ["subject", "subject_name"], "")
                    : "";

                return `
                    <li>
                        <strong>${index + 1}. ${escapeHTML(topic)}</strong>

                        ${subject
                            ? `<p>Subject: ${escapeHTML(subject)}</p>`
                            : ""}

                        ${description
                            ? `<p>${escapeHTML(description)}</p>`
                            : ""}

                        ${hours !== null
                            ? `<p>Estimated time: ${
                                escapeHTML(formatHours(hours))
                            }</p>`
                            : ""}
                    </li>
                `;
            })}
           </ol>`
        : `<p>
            No roadmap topics were returned. Check the school curriculum
            data and backend response.
           </p>`;

    const studySessionsHTML = renderSchoolWeeklyPlan(sessions, weeklyHours);

    if (!resultsContent || !resultsSection) {
        showMessage(
            "The results section is missing from index.html.",
            "error"
        );
        return;
    }

    const board = profile.school_board ||
        schoolAnalysis.board ||
        schoolAnalysis.school_board ||
        "N/A";

    const studentClass = profile.school_class ??
        schoolAnalysis.school_class ??
        schoolAnalysis.class ??
        "N/A";

    const stream = profile.school_stream ||
        schoolAnalysis.stream ||
        schoolAnalysis.school_stream ||
        "N/A";

    const goal = profile.school_goal ||
        schoolAnalysis.goal ||
        schoolAnalysis.school_goal ||
        "N/A";

    const learningStyle = profile.learning_style ||
        schoolAnalysis.learning_style ||
        "N/A";

    const studentName = profile.name ||
        schoolAnalysis.name ||
        "Student";

    // The school plan is a list of sessions, so totals come from the sessions.
    const plannedHoursSum = sessions.reduce((sum, session) => {
        const hours = Number(
            getField(session, ["hours", "estimated_hours"], 0)
        );
        return sum + (Number.isFinite(hours) ? hours : 0);
    }, 0);

    const totalStudyHours = plannedHoursSum > 0 ? plannedHoursSum : null;
    const plannedWeeks = groupSchoolSessionsByWeek(sessions, weeklyHours).length;

    resultsContent.innerHTML = `
        <div class="result-overview">
            <article class="result-stat">
                <p>Education Level</p>
                <h3>Class ${escapeHTML(studentClass)}</h3>
            </article>

            <article class="result-stat">
                <p>Subjects Selected</p>
                <h3>${subjects.length}</h3>
            </article>

            <article class="result-stat">
                <p>Weekly Study Time</p>
                <h3>${escapeHTML(formatNumber(weeklyHours))} hrs</h3>
            </article>
        </div>

        <div class="result-panel">
            <h3>School Student Profile</h3>

            <ul class="result-list">
                <li><strong>Student:</strong>
                    ${escapeHTML(studentName)}
                </li>
                <li><strong>Board:</strong>
                    ${escapeHTML(board)}
                </li>
                <li><strong>Class:</strong>
                    ${escapeHTML(studentClass)}
                </li>
                <li><strong>Group:</strong>
                    ${escapeHTML(stream)}
                </li>
                <li><strong>Learning Goal:</strong>
                    ${escapeHTML(goal)}
                </li>
                <li><strong>Learning Style:</strong>
                    ${escapeHTML(learningStyle)}
                </li>
            </ul>
        </div>

        <div class="result-panel">
            <h3>Your Selected Subjects</h3>

            <p>
                ${subjects.length
                    ? subjects.map(subject => `
                        <span class="result-tag">
                            ${escapeHTML(subject)}
                        </span>
                    `).join(" ")
                    : "No subjects were returned."}
            </p>
        </div>

        <div class="result-panel">
            <h3>Your School Learning Roadmap</h3>

            ${renderSchoolSubjectChart(roadmap)}

            ${roadmapHTML}

            ${totalHours !== null
                ? `<p><strong>Estimated total:</strong>
                    ${escapeHTML(formatHours(totalHours))}
                   </p>`
                : ""}
        </div>

        <div class="result-panel">
            <h3>Recommended School Resources</h3>
            ${renderResourceList(resources, true)}
        </div>

        <div class="result-panel">
            <h3>Your Study Plan</h3>

            <p><strong>Weekly study time:</strong>
                ${escapeHTML(formatHours(weeklyHours))}
            </p>

            ${totalStudyHours !== null
                ? `<p><strong>Total planned hours:</strong>
                    ${escapeHTML(formatHours(totalStudyHours))}
                   </p>`
                : ""}

            ${plannedWeeks > 0
                ? `<p><strong>Estimated duration:</strong>
                    ${escapeHTML(plannedWeeks)} weeks
                   </p>`
                : ""}

            ${renderSchoolPlanBreakdown(sessions)}

            <h4>Weekly Plan</h4>
            ${studySessionsHTML}
        </div>
    `;

    animateCharts();
    resultsSection.classList.remove("hidden");

    resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

// ==================================================
// DISPLAY COLLEGE RESULTS
// ==================================================

function renderResults(data) {
    if (!resultsContent || !resultsSection) {
        showMessage(
            "The results section is missing from index.html.",
            "error"
        );
        return;
    }

    resultsContent.innerHTML = [
        renderOverview(data),
        renderCareerPredictions(data),
        renderSkillGaps(data),
        renderRoadmap(data),
        renderResources(data),
        renderStudyPlan(data)
    ].join("");

    animateCharts();
    resultsSection.classList.remove("hidden");

    resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

// ==================================================
// FORM SUBMISSION AND BACKEND CONNECTION
// ==================================================

if (studentForm) {
    studentForm.addEventListener("submit", async event => {
        event.preventDefault();

        if (!studentForm.reportValidity()) {
            return;
        }

        const name = getElementValue("student-name");
        const stage = educationStage ? educationStage.value : "";

        const weeklyHours = Number(getElementValue("weekly-hours"));
        const learningStyle = getElementValue("learning-style");

        const currentSkills = parseSkills(
            getElementValue("current-skills")
        );

        const interests = getElementValue("interests")
            .split(",")
            .map(item => item.trim())
            .filter(Boolean);

        if (
            !Number.isFinite(weeklyHours) ||
            weeklyHours < 1 ||
            weeklyHours > 80
        ) {
            showMessage(
                "Please enter weekly study hours between 1 and 80.",
                "error"
            );
            return;
        }

        const isSchool = stage === "School";
        let studentProfile;

        if (isSchool) {
            if (
                !schoolBoard ||
                !schoolClass ||
                !schoolGoal ||
                !schoolSubjects ||
                !schoolStream
            ) {
                showMessage(
                    "School form fields are missing from index.html.",
                    "error"
                );
                return;
            }

            const subjects = schoolSubjects.value
                .split(",")
                .map(item => item.trim())
                .filter(Boolean);

            if (
                !schoolBoard.value ||
                !schoolClass.value ||
                !schoolGoal.value
            ) {
                showMessage(
                    "Please select your board, class, and learning goal.",
                    "error"
                );
                return;
            }

            if (!subjects.length) {
                showMessage(
                    "Please enter at least one school subject, separated by commas.",
                    "error"
                );
                schoolSubjects.focus();
                return;
            }

            studentProfile = {
                name,
                education_stage: "School",
                school_board: schoolBoard.value,
                school_class: Number(schoolClass.value),
                school_stream: schoolStream.value,
                school_subjects: subjects,
                school_goal: schoolGoal.value,
                current_skills: currentSkills,
                interests,
                weekly_learning_hours: weeklyHours,
                learning_style: learningStyle
            };
        } else {
            if (
                !degree ||
                !department ||
                !studyYear ||
                !careerGoal
            ) {
                showMessage(
                    "College form fields are missing from index.html.",
                    "error"
                );
                return;
            }

            if (
                !degree.value ||
                !department.value ||
                !studyYear.value ||
                !careerGoal.value
            ) {
                showMessage(
                    "Please complete your degree, department, study year, and career goal.",
                    "error"
                );
                return;
            }

            studentProfile = {
                name,
                education_stage: stage,
                degree: degree.value,
                department: department.value,
                study_year: Number(studyYear.value),
                current_skills: currentSkills,
                interests,
                career_goal: careerGoal.value,
                weekly_learning_hours: weeklyHours,
                learning_style: learningStyle
            };
        }

        if (analyzeButton) {
            analyzeButton.disabled = true;
            analyzeButton.textContent = isSchool
                ? "Creating Your Learning Roadmap..."
                : "Analyzing Your Profile...";
        }

        showMessage(
            isSchool
                ? "Preparing your school learning recommendations..."
                : "Connecting to EduPath AI and analyzing your profile..."
        );

        if (resultsSection) {
            resultsSection.classList.add("hidden");
        }

        try {
            const response = await fetch(
                `${API_BASE_URL}/api/analyze`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(studentProfile)
                }
            );

            let data;

            try {
                data = await response.json();
            } catch {
                throw new Error(
                    "The backend returned an invalid response. Check the Flask server."
                );
            }

            if (!response.ok || data.success !== true) {
                throw new Error(
                    data.error ||
                    `Analysis failed (HTTP ${response.status}).`
                );
            }

            if (isSchool) {
                renderSchoolResults(data, studentProfile);
            } else {
                renderResults(data);
            }

            showMessage(
                "Analysis completed successfully!",
                "success"
            );
        } catch (error) {
            console.error("EduPath AI analysis error:", error);

            if (error instanceof TypeError) {
                showMessage(
                    "Cannot connect to the backend. Make sure Flask is running at http://127.0.0.1:5000.",
                    "error"
                );
            } else {
                showMessage(
                    error.message || "Something went wrong. Please try again.",
                    "error"
                );
            }
        } finally {
            if (analyzeButton) {
                analyzeButton.disabled = false;
                analyzeButton.textContent = isSchool
                    ? "Create My Learning Roadmap →"
                    : "Analyze My Profile →";
            }
        }
    });
} else {
    console.error(
        "EduPath AI: Form with id 'student-form' was not found in index.html."
    );
}
// ==================================================
// DOWNLOAD PDF (browser print -> Save as PDF)
// ==================================================

const downloadPdfButton = document.getElementById("download-pdf-button");
const originalPageTitle = document.title;

if (downloadPdfButton) {
    downloadPdfButton.addEventListener("click", () => {
        window.print();
    });
}

window.addEventListener("beforeprint", () => {
    // show every week of the study plan in the PDF
    document.querySelectorAll("#results details").forEach((item) => {
        if (!item.open) {
            item.dataset.openedForPrint = "true";
            item.open = true;
        }
    });

    // the PDF file name comes from the page title
    const nameInput = document.getElementById("student-name");
    const studentName = nameInput ? nameInput.value.trim() : "";
    document.title = studentName
        ? `EduPath-AI-Report-${studentName.replace(/\s+/g, "-")}`
        : "EduPath-AI-Report";
});

window.addEventListener("afterprint", () => {
    document.querySelectorAll("#results details").forEach((item) => {
        if (item.dataset.openedForPrint) {
            item.open = false;
            delete item.dataset.openedForPrint;
        }
    });
    document.title = originalPageTitle;
});