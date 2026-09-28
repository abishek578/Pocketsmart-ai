async function apiJSON(url, options = {}) {
    const r = await fetch(url, {
        credentials: "same-origin",
        ...options
    });

    const d = await r.json().catch(() => ({}));

    if (!r.ok) {
        throw new Error(d.detail || "Request failed.");
    }

    return d;
}


function money(v) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0
    }).format(v || 0);
}


function esc(v) {
    return String(v ?? "").replace(
        /[&<>"']/g,
        c => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        }[c])
    );
}


function itemCard(i) {
    const links = Object.entries(i.shopping_links || {})
        .map(
            ([n, u]) =>
                `<a class="chip" target="_blank" rel="noopener noreferrer" href="${esc(u)}">${esc(n)}</a>`
        )
        .join("");

    return `
        <article class="recommendation">
            <div>
                <span class="tag">${esc(i.item_type)}</span>
                <h4>${esc(i.name)}</h4>
                <p>${esc(i.description)}</p>
            </div>

            <div class="price">
                ${money(i.estimated_price)} × ${i.quantity}
            </div>

            <div class="chips">
                ${links}
            </div>

            <small>
                Search: ${esc(i.search_terms)}
            </small>
        </article>
    `;
}


function renderResult(data) {
    const r = data.result;

    const cats = (r.budget_breakdown || [])
        .map(
            c => `
                <section class="result-category">
                    <div class="panel-head">
                        <h3>${esc(c.category)}</h3>
                        <strong>${money(c.allocation)}</strong>
                    </div>

                    ${(c.items || []).map(itemCard).join("")}
                </section>
            `
        )
        .join("");


    const warnings = (r.warnings || [])
        .map(w => `<li>${esc(w)}</li>`)
        .join("");


    const tips = (r.styling_tips || [])
        .map(t => `<li>${esc(t)}</li>`)
        .join("");


    /*
     * Format Gemini's outfit analysis into readable information
     * instead of displaying the raw JSON object.
     */
    let outfitAnalysis = "";

    if (r.outfit_analysis) {
        const outfit = r.outfit_analysis;

        if (typeof outfit === "object" && outfit !== null) {
            const colors = Array.isArray(outfit.colors)
                ? outfit.colors
                : [];

            const style = outfit.style || "";
            const formality = outfit.formality || "";

            outfitAnalysis = `
                <div class="info-box outfit-analysis">

                    <strong>Outfit analysis</strong>

                    ${
                        colors.length
                            ? `
                                <div class="outfit-detail">
                                    <span class="outfit-label">
                                        Colors
                                    </span>

                                    <span>
                                        ${colors
                                            .map(color => esc(color))
                                            .join(", ")}
                                    </span>
                                </div>
                            `
                            : ""
                    }

                    ${
                        style
                            ? `
                                <div class="outfit-detail">
                                    <span class="outfit-label">
                                        Style
                                    </span>

                                    <span>
                                        ${esc(style)}
                                    </span>
                                </div>
                            `
                            : ""
                    }

                    ${
                        formality
                            ? `
                                <div class="outfit-detail">
                                    <span class="outfit-label">
                                        Formality
                                    </span>

                                    <span>
                                        ${esc(formality)}
                                    </span>
                                </div>
                            `
                            : ""
                    }

                </div>
            `;
        } else {
            outfitAnalysis = `
                <div class="info-box outfit-analysis">
                    <strong>Outfit analysis</strong>

                    <p>
                        ${esc(String(outfit))}
                    </p>
                </div>
            `;
        }
    }


    return `
        <div class="panel result-summary">

            <div class="panel-head">

                <div>
                    <span class="tag">
                        ${esc(r.mode)} mode
                    </span>

                    <h2>
                        Your recommendation
                    </h2>
                </div>

                <div>
                    <strong>
                        ${money(r.remaining_budget)}
                    </strong>

                    <small>
                        remaining
                    </small>
                </div>

            </div>


            ${outfitAnalysis}


            ${
                warnings
                    ? `
                        <div class="warning">

                            <strong>
                                Notes
                            </strong>

                            <ul>
                                ${warnings}
                            </ul>

                        </div>
                    `
                    : ""
            }


            ${
                tips
                    ? `
                        <div class="info-box">

                            <strong>
                                Tips
                            </strong>

                            <ul>
                                ${tips}
                            </ul>

                        </div>
                    `
                    : ""
            }

        </div>

        ${cats}
    `;
}


function showError(e) {
    document.querySelector("#results").innerHTML = `
        <div class="warning">

            <strong>
                Error
            </strong>

            <p>
                ${esc(e.message)}
            </p>

        </div>
    `;
}


function addHomeItem(category = "", quantity = 1) {
    const w = document.querySelector("#home-items");

    const row = document.createElement("div");

    row.className = "item-row";

    row.innerHTML = `
        <input
            name="item_category"
            placeholder="e.g. ceiling light"
            value="${esc(category)}"
            required
        >

        <input
            name="item_quantity"
            type="number"
            min="1"
            max="50"
            value="${quantity}"
            required
        >

        <button
            type="button"
            class="button danger small"
            onclick="this.parentElement.remove()"
        >
            Remove
        </button>
    `;

    w.appendChild(row);
}


document.addEventListener("DOMContentLoaded", () => {
    const homeItems = document.querySelector("#home-items");

    if (
        homeItems &&
        !homeItems.children.length
    ) {
        addHomeItem("ceiling light", 2);
        addHomeItem("curtain", 2);
        addHomeItem("side table", 2);
    }
});


function initHomePlanner() {
    document
        .querySelector("#home-form")
        .addEventListener("submit", async e => {

            e.preventDefault();

            const f = new FormData(e.target);

            const cats = [
                ...document.querySelectorAll(
                    "[name=item_category]"
                )
            ];

            const qty = [
                ...document.querySelectorAll(
                    "[name=item_quantity]"
                )
            ];


            const p = {
                total_budget: Number(
                    f.get("total_budget")
                ),

                rooms: f
                    .get("rooms")
                    .split(",")
                    .map(x => x.trim())
                    .filter(Boolean),

                items: cats.map((x, i) => ({
                    category: x.value,
                    quantity: Number(
                        qty[i].value
                    )
                })),

                style: f.get("style"),

                additional_requirements:
                    f.get(
                        "additional_requirements"
                    )
            };


            try {
                document.querySelector(
                    "#results"
                ).innerHTML =
                    `<div class="panel">Generating...</div>`;


                const result = await apiJSON(
                    "/generate-home",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify(p)
                    }
                );


                document.querySelector(
                    "#results"
                ).innerHTML =
                    renderResult(result);

            } catch (e) {
                showError(e);
            }
        });
}


function initPartyPlanner() {
    document
        .querySelector("#party-form")
        .addEventListener("submit", async e => {

            e.preventDefault();

            const f = new FormData(e.target);


            const p = {
                total_budget: Number(
                    f.get("total_budget")
                ),

                guest_count: Number(
                    f.get("guest_count")
                ),

                event_type:
                    f.get("event_type"),

                venue_type:
                    f.get("venue_type"),

                city:
                    f.get("city"),

                catering_needed:
                    f.get("catering_needed") ===
                    "on",

                decoration_needed:
                    f.get("decoration_needed") ===
                    "on",

                entertainment_needed:
                    f.get(
                        "entertainment_needed"
                    ) === "on",

                additional_requirements:
                    f.get(
                        "additional_requirements"
                    )
            };


            try {
                document.querySelector(
                    "#results"
                ).innerHTML =
                    `<div class="panel">Generating...</div>`;


                const result = await apiJSON(
                    "/generate-party",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify(p)
                    }
                );


                document.querySelector(
                    "#results"
                ).innerHTML =
                    renderResult(result);

            } catch (e) {
                showError(e);
            }
        });
}


function initJewelryPlanner() {
    document
        .querySelector("#jewelry-form")
        .addEventListener("submit", async e => {

            e.preventDefault();

            try {
                document.querySelector(
                    "#results"
                ).innerHTML =
                    `<div class="panel">Analyzing...</div>`;


                const result = await apiJSON(
                    "/generate-jewelry",
                    {
                        method: "POST",

                        body: new FormData(
                            e.target
                        )
                    }
                );


                document.querySelector(
                    "#results"
                ).innerHTML =
                    renderResult(result);

            } catch (e) {
                showError(e);
            }
        });
}


async function loadHistory() {
    try {
        const rows = await apiJSON(
            "/history"
        );

        const c =
            document.querySelector(
                "#history-list"
            );


        if (!rows.length) {
            c.innerHTML = `
                <div class="panel">
                    <p>
                        No recommendations yet.
                    </p>
                </div>
            `;

            return;
        }


        c.innerHTML = rows
            .map(
                r => `
                    <a
                        class="history-card"
                        href="/recommendation/${r.id}"
                    >

                        <span class="tag">
                            ${esc(r.planner_type)}
                        </span>

                        <h3>
                            Recommendation #${r.id}
                        </h3>

                        <p>
                            ${new Date(
                                r.created_at
                            ).toLocaleString()}
                        </p>

                    </a>
                `
            )
            .join("");

    } catch (e) {
        document.querySelector(
            "#history-list"
        ).innerHTML = `
            <div class="warning">
                ${esc(e.message)}
            </div>
        `;
    }
}