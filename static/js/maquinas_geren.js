let allMachines = []

document.addEventListener("DOMContentLoaded", () => {
  initializeManagement()
})

function initializeManagement() {
  // Store all machine cards
  allMachines = Array.from(document.querySelectorAll(".machine-card"))

  // Setup event listeners
  setupEventListeners()

  // Setup keyboard shortcuts
  setupKeyboardShortcuts()
}

function setupEventListeners() {
  // Exit button
  const btnSair = document.getElementById("btnSair")
  if (btnSair) {
    btnSair.addEventListener("click", handleExit)
  }

  // Search input
  const searchInput = document.getElementById("searchInput")
  if (searchInput) {
    searchInput.addEventListener("input", handleSearch)
  }

  // Filter select
  const tipoMaquina = document.getElementById("tipoMaquina")
  if (tipoMaquina) {
    tipoMaquina.addEventListener("change", handleFilter)
  }

  // Add button
  const btnAdicionar = document.getElementById("btnAdicionar")
  if (btnAdicionar) {
    btnAdicionar.addEventListener("click", handleAddMachine)
  }

  // Menu items
  const menuItems = document.querySelectorAll(".menu-item")
  menuItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      if (this.getAttribute("href") === "#") {
        e.preventDefault()
        showNotification("Funcionalidade em desenvolvimento", "info")
      }
    })
  })

  // Action buttons on machine cards
  const actionButtons = document.querySelectorAll(".action-btn")
  actionButtons.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.stopPropagation()
      const action = this.getAttribute("data-action")
      const card = this.closest(".machine-card")
      const machineCode = card.querySelector(".machine-code").textContent
      handleMachineAction(action, machineCode)
    })
  })

  // Machine card click
  const machineCards = document.querySelectorAll(".machine-card")
  machineCards.forEach((card) => {
    card.addEventListener("click", function () {
      const machineCode = this.querySelector(".machine-code").textContent
      const status = this.querySelector(".machine-status").textContent
      showNotification(`Máquina ${machineCode} - ${status}`, "info")
    })
  })
}

function handleSearch(e) {
  const searchTerm = e.target.value.toLowerCase().trim()
  const machinesGrid = document.getElementById("machinesGrid")

  allMachines.forEach((card) => {
    const machineCode = card.getAttribute("data-code")
    if (machineCode.includes(searchTerm)) {
      card.style.display = "flex"
    } else {
      card.style.display = "none"
    }
  })

  // Check if any machines are visible
  const visibleMachines = allMachines.filter((card) => card.style.display !== "none")
  if (visibleMachines.length === 0 && searchTerm !== "") {
    showNotification("Nenhuma máquina encontrada", "info")
  }
}

function handleFilter(e) {
  const filterValue = e.target.value
  if (filterValue) {
    showNotification(`Filtrando por: ${filterValue}`, "info")
    // Here you would implement actual filtering logic based on machine type
  } else {
    // Reset filter
    allMachines.forEach((card) => {
      card.style.display = "flex"
    })
  }
}

function handleAddMachine() {
  showNotification("Abrindo formulário de cadastro...", "success")
  // Here you would open a modal or navigate to add machine form
}

function handleMachineAction(action, machineCode) {
  switch (action) {
    case "manutencao":
      showNotification(`Abrindo manutenção para máquina ${machineCode}`, "info")
      break
    case "detalhes":
      showNotification(`Visualizando detalhes da máquina ${machineCode}`, "info")
      break
    case "menu":
      showNotification(`Opções da máquina ${machineCode}`, "info")
      break
    default:
      showNotification("Ação não reconhecida", "error")
  }
}

function handleExit() {
  if (confirm("Tem certeza que deseja sair?")) {
    showNotification("Saindo do sistema...", "success")
    setTimeout(() => {
      window.location.href = "/login.html"
    }, 1000)
  }
}

function setupKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Ctrl+Q to exit
    if (e.ctrlKey && e.key === "q") {
      e.preventDefault()
      handleExit()
    }

    // Ctrl+F to focus search
    if (e.ctrlKey && e.key === "f") {
      e.preventDefault()
      const searchInput = document.getElementById("searchInput")
      if (searchInput) {
        searchInput.focus()
      }
    }

    // Ctrl+N to add new machine
    if (e.ctrlKey && e.key === "n") {
      e.preventDefault()
      handleAddMachine()
    }
  })
}

function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  notification.className = `notification notification-${type}`
  notification.textContent = message

  const container = document.getElementById("notificationContainer")
  if (container) {
    container.appendChild(notification)

    setTimeout(() => {
      notification.style.animation = "slideIn 0.3s ease reverse"
      setTimeout(() => {
        notification.remove()
      }, 300)
    }, 3000)
  }
}

// Export functions for external use
window.machineManagement = {
  showNotification,
  handleAddMachine,
  handleExit,
}