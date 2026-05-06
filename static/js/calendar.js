const events = [
    {
        id: 1,
        title: "Bentonville Cars & Coffee",
        type: "Cars & Coffee",
        date: "2026-05-10",
        time: "8:00 AM",
        location: "Bentonville Square",
        description: "Monthly cars and coffee meetup at the Bentonville Square. All makes and models welcome."
    },
    {
        id: 2,
        title: "NWA Spring Car Show",
        type: "Car Show",
        date: "2026-05-17",
        time: "10:00 AM",
        location: "Rogers, AR",
        description: "Annual spring car show featuring vehicles from across Northwest Arkansas."
    },
    {
        id: 3,
        title: "Saturday Night Cruise",
        type: "Cruise",
        date: "2026-05-11",
        time: "7:00 PM",
        location: "Fayetteville, AR",
        description: "Casual evening cruise through Fayetteville. Meet at the Walmart AMP parking lot."
    }
];

let currentDate = new Date();
let currentView = "month";

const monthNames = ["January","February","March","April","May","June",
                    "July","August","September","October","November","December"];
const dayNames = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];

function getEventsForDate(dateStr) {
    return events.filter(e => e.date === dateStr);
}

function formatDateStr(year, month, day) {
    return `${year}-${String(month+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
}

function renderMonth() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const today = new Date();

    document.getElementById("monthYear").textContent = `${monthNames[month]} ${year}`;

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const daysInPrevMonth = new Date(year, month, 0).getDate();

    let html = '<div class="month-grid">';
    dayNames.forEach(d => html += `<div class="day-header">${d}</div>`);

    for (let i = 0; i < firstDay; i++) {
        const day = daysInPrevMonth - firstDay + i + 1;
        html += `<div class="day-cell other-month"><div class="day-number">${day}</div></div>`;
    }

    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = formatDateStr(year, month, d);
        const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
        const dayEvents = getEventsForDate(dateStr);

        html += `<div class="day-cell ${isToday ? 'today' : ''}">
                    <div class="day-number">${d}</div>`;
        dayEvents.forEach(e => {
            html += `<div class="cal-event" onclick="openPopup(${e.id})">${e.title}</div>`;
        });
        html += `</div>`;
    }

    const totalCells = firstDay + daysInMonth;
    const remaining = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
    for (let i = 1; i <= remaining; i++) {
        html += `<div class="day-cell other-month"><div class="day-number">${i}</div></div>`;
    }

    html += '</div>';
    document.getElementById("calendarView").innerHTML = html;
}

function renderWeek() {
    const today = new Date();
    const startOfWeek = new Date(currentDate);
    const day = currentDate.getDay();
    startOfWeek.setDate(currentDate.getDate() - day);

    const weekDates = [];
    for (let i = 0; i < 7; i++) {
        const d = new Date(startOfWeek);
        d.setDate(startOfWeek.getDate() + i);
        weekDates.push(d);
    }

    const firstDay = weekDates[0];
    const lastDay = weekDates[6];
    const sameMonth = firstDay.getMonth() === lastDay.getMonth();
    const label = sameMonth
        ? `${monthNames[firstDay.getMonth()]} ${firstDay.getFullYear()}`
        : `${monthNames[firstDay.getMonth()]} – ${monthNames[lastDay.getMonth()]} ${lastDay.getFullYear()}`;

    document.getElementById("monthYear").textContent = label;

    let html = '<div class="week-grid"><div class="week-header">';
    weekDates.forEach(d => {
        const isToday = d.toDateString() === today.toDateString();
        html += `<div class="week-day-header ${isToday ? 'today' : ''}">
                    ${dayNames[d.getDay()]}
                    <span>${d.getDate()}</span>
                </div>`;
    });
    html += '</div><div class="week-body">';

    weekDates.forEach(d => {
        const dateStr = formatDateStr(d.getFullYear(), d.getMonth(), d.getDate());
        const dayEvents = getEventsForDate(dateStr);
        const isToday = d.toDateString() === today.toDateString();
        html += `<div class="week-cell ${isToday ? 'today' : ''}">`;
        dayEvents.forEach(e => {
            html += `<div class="cal-event" onclick="openPopup(${e.id})">${e.title}</div>`;
        });
        html += `</div>`;
    });

    html += '</div></div>';
    document.getElementById("calendarView").innerHTML = html;
}

function render() {
    if (currentView === "month") renderMonth();
    else renderWeek();
}

function openPopup(id) {
    const e = events.find(ev => ev.id === id);
    if (!e) return;
    document.getElementById("popupType").textContent = e.type;
    document.getElementById("popupTitle").textContent = e.title;
    document.getElementById("popupMeta").textContent = `${e.date} · ${e.time} · ${e.location}`;
    document.getElementById("popupDesc").textContent = e.description;
    document.getElementById("popupOverlay").classList.add("active");
}

document.getElementById("popupClose").addEventListener("click", () => {
    document.getElementById("popupOverlay").classList.remove("active");
});

document.getElementById("popupOverlay").addEventListener("click", (e) => {
    if (e.target === document.getElementById("popupOverlay")) {
        document.getElementById("popupOverlay").classList.remove("active");
    }
});

document.getElementById("prevBtn").addEventListener("click", () => {
    if (currentView === "month") currentDate.setMonth(currentDate.getMonth() - 1);
    else currentDate.setDate(currentDate.getDate() - 7);
    render();
});

document.getElementById("nextBtn").addEventListener("click", () => {
    if (currentView === "month") currentDate.setMonth(currentDate.getMonth() + 1);
    else currentDate.setDate(currentDate.getDate() + 7);
    render();
});

document.getElementById("monthBtn").addEventListener("click", () => {
    currentView = "month";
    document.getElementById("monthBtn").classList.add("active");
    document.getElementById("weekBtn").classList.remove("active");
    render();
});

document.getElementById("weekBtn").addEventListener("click", () => {
    currentView = "week";
    document.getElementById("weekBtn").classList.add("active");
    document.getElementById("monthBtn").classList.remove("active");
    render();
});

render();