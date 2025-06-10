document.addEventListener("DOMContentLoaded", function () {
    const banner = document.getElementById("cookie-banner");

    if (banner) {
        document.getElementById("btn-accept").addEventListener("click", () => {
            setConsent("accepted");
        });
        document.getElementById("btn-reject").addEventListener("click", () => {
            setConsent("rejected");
        });
    }

    function setConsent(decision) {
        fetch(`/set-consent/${decision}`)
            .then(() => {
                document.getElementById("cookie-banner").style.display = "none";
                location.reload();  // Aplica los cambios recargando
            });
    }
});
