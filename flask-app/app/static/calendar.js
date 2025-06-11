// Objeto principal para gestionar el estado del calendario y reservas
const calendar = {
    currentMonth: new Date().getMonth(),
    currentYear: new Date().getFullYear(),
    reservations: {},
    availableHours: [],
    occupiedHours: new Set(),
    selectedDate: null,
    selectedHour: null,
    tipoPista: null,
};

// Cambia el tipo de pista seleccionado y recarga el calendario
function setTipoPista(tipo) {
    calendar.tipoPista = tipo;
    document.getElementById("selectedDate").textContent = "";
    loadCalendar();
}

// Carga las reservas del club seleccionado desde el backend
async function loadReservas() {
    const clubId = document.getElementById('club').value;
    const response = await fetch(`/api/reservas?club_id=${clubId}`);
    const data = await response.json();

    calendar.reservations = data.reservas;
    calendar.availableHours = data.horas_disponibles;
    calendar.occupiedHours = new Set(data.horas_ocupadas);
}

// Genera el calendario de días del mes actual
function loadCalendar() {
    const monthName = document.getElementById("monthName");
    const daysContainer = document.getElementById("days");

    const firstDay = new Date(calendar.currentYear, calendar.currentMonth, 1);
    const lastDay = new Date(calendar.currentYear, calendar.currentMonth + 1, 0);
    const today = new Date();

    monthName.textContent = firstDay.toLocaleString("es-ES", { month: "long", year: "numeric" }).toUpperCase();
    daysContainer.innerHTML = "";

    const daysGrid = document.createElement("div");
    daysGrid.classList.add("days-grid");

    // Calcula el índice del primer día del mes (lunes=0)
    const firstDayIndex = (firstDay.getDay() + 6) % 7;

    // Añade días vacíos al principio si el mes no empieza en lunes
    for (let i = 0; i < firstDayIndex; i++) {
        const emptyDay = document.createElement("div");
        emptyDay.classList.add("day", "empty");
        daysGrid.appendChild(emptyDay);
    }

    // Genera los días del mes
    for (let i = 1; i <= lastDay.getDate(); i++) {
        const day = document.createElement("div");
        const dateKey = `${calendar.currentYear}-${String(calendar.currentMonth + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
        const currentDate = new Date(calendar.currentYear, calendar.currentMonth, i);
        const nombreDia = currentDate.toLocaleDateString("es-ES", { weekday: "short" });

        day.innerHTML = `<div class="nombre-dia">${nombreDia}</div><div>${i}</div>`;
        day.classList.add("day");

        // Deshabilita días pasados
        if (currentDate < today.setHours(0, 0, 0, 0)) {
            day.classList.add("disabled");
        } else {
            day.addEventListener("click", () => selectDay(dateKey, day));
        }

        daysGrid.appendChild(day);
    }

    daysContainer.appendChild(daysGrid);
}

// Selecciona un día y carga las horas disponibles para ese día
function selectDay(dateKey, dayElement) {
    calendar.selectedDate = dateKey;

    document.querySelectorAll(".day").forEach(day => day.classList.remove("selected"));
    dayElement.classList.add("selected");

    loadHours(dateKey);
}

// Carga los botones de horas disponibles para el día seleccionado
function loadHours(dateKey) {
    const morningSlots = document.getElementById("morningSlots");
    const afternoonSlots = document.getElementById("afternoonSlots");
    morningSlots.innerHTML = "";
    afternoonSlots.innerHTML = "";

    const today = new Date().toISOString().split("T")[0];
    const currentTime = new Date().toTimeString().split(" ")[0].substring(0, 5);

    // Filtra horas si es hoy (no mostrar horas pasadas)
    const filteredHours = dateKey === today
        ? calendar.availableHours.filter(hour => hour >= currentTime)
        : calendar.availableHours;

    const morningHours = ["10:00", "11:00", "12:00", "13:00"];
    const afternoonHours = ["16:00", "17:00", "18:00", "19:00", "20:00", "21:00"];

    const selectedDateObj = new Date(dateKey);
    const isSunday = selectedDateObj.getDay() === 0;

    // Crea los botones de horas y los coloca en la franja correspondiente
    filteredHours.forEach(hour => {
        const key = `${dateKey}-${hour}`;
        const hourElement = document.createElement("button");
        hourElement.textContent = hour;
        hourElement.classList.add("hour-slot");

        if (calendar.occupiedHours.has(key)) {
            hourElement.classList.add("reserved");
            hourElement.disabled = true;
        } else {
            hourElement.addEventListener("click", () => selectHour(hourElement, hour));
        }

        if (isSunday && morningHours.includes(hour)) {
            morningSlots.appendChild(hourElement);
        } else if (!isSunday && afternoonHours.includes(hour)) {
            afternoonSlots.appendChild(hourElement);
        } else if (!isSunday && morningHours.includes(hour)) {
            morningSlots.appendChild(hourElement);
        }
    });
}

// Selecciona una hora y muestra el resumen de la reserva
function selectHour(hourElement, hour) {
    calendar.selectedHour = hour;

    document.querySelectorAll(".hour-slot").forEach(slot => slot.classList.remove("selected"));
    hourElement.classList.add("selected");

    const tipoPista = document.querySelector('input[name="tipoPista"]:checked').value;
    const tipoPistaTexto = tipoPista === "pista2" ? "Pista para dos personas" : "Pista para cuatro personas";

    const [year, month, day] = calendar.selectedDate.split("-");
    const formattedDate = `${day}/${month}/${year}`;

    document.getElementById("resumenTexto").textContent =
        `Fecha: ${formattedDate}, Hora: ${hour}, Tipo de pista: ${tipoPistaTexto}`;
    document.getElementById("resumen").style.display = "block";
}

// Envía la reserva al backend y muestra el resultado
async function confirmarReserva() {
    if (!calendar.selectedDate || !calendar.selectedHour) {
        alert("Por favor, selecciona una fecha y una hora antes de confirmar la reserva.");
        return;
    }
    const tipoPista = document.querySelector('input[name="tipoPista"]:checked').value;
    const clubId = document.getElementById('club').value;

    const response = await fetch('/api/reservas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            club_id: clubId,
            fecha: calendar.selectedDate,
            hora: calendar.selectedHour,
            pista: tipoPista
        }),
    });

    const data = await response.json();
    if (data.error) {
        alert(data.error);
    } else {
        alert(data.message);
        location.reload();
    }
}

// Cambia el mes mostrado en el calendario
function changeMonth(offset) {
    calendar.currentMonth += offset;

    if (calendar.currentMonth < 0) {
        calendar.currentMonth = 11;
        calendar.currentYear -= 1;
    } else if (calendar.currentMonth > 11) {
        calendar.currentMonth = 0;
        calendar.currentYear += 1;
    }

    loadCalendar();
}

// Inicializa el calendario y carga las reservas al cargar la página
document.addEventListener("DOMContentLoaded", async () => {
    await loadReservas();
    loadCalendar();
});
