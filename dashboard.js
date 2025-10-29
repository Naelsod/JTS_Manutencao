
let activeMenu = "Dashboard"


document.addEventListener("DOMContentLoaded", () => {
  initializeDashboard()
})


function initializeDashboard() {

  animateNumbers()

 
  setupEventListeners()


  setupKeyboardShortcuts()


  setInterval(updateTimestamps, 60000)
}

function setupEventListeners() {
  
  const btnSair = document.getElementById("btnSair")
  if (btnSair) {
    btnSair.addEventListener("click", handleExit)
  }


  const menuItems = document.querySelectorAll(".menu-item")
  menuItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      e.preventDefault()
      const menuName = this.getAttribute("data-menu")
      handleMenuClick(menuName, this)
    })
  })

 
  const atividadeItems = document.querySelectorAll(".atividade-item")
  atividadeItems.forEach((item) => {
    item.addEventListener("click", function () {
      const machine = this.getAttribute("data-machine")
      const status = this.getAttribute("data-status")
      handleActivityClick(machine, status)
    })
  })

  const contatoItems = document.querySelectorAll(".contato-item")
  contatoItems.forEach((item) => {
    item.addEventListener("click", function () {
      const name = this.getAttribute("data-name")
      const phone = this.getAttribute("data-phone")
      handleContactClick(name, phone)
    })
  })
}


function animateNumbers() {
  const numbers = document.querySelectorAll(".stats-number")

  numbers.forEach((num) => {
    const target = Number.parseInt(num.textContent)
    let current = 0
    const increment = target / 30

    const timer = setInterval(() => {
      current += increment
      if (current >= target) {
        num.textContent = target
        clearInterval(timer)
      } else {
        num.textContent = Math.floor(current)
      }
    }, 30)
  })
}


function handleMenuClick(menuName, element) {
  
  document.querySelectorAll(".menu-item").forEach((item) => {
    item.classList.remove("active")
  })

  
  element.classList.add("active")

  // Atualizar estado
  activeMenu = menuName

  
  showNotification(`Navegando para ${menuName}`, "info")
}

// Manipular clique em atividade
function handleActivityClick(machine, status) {
  showNotification(`Máquina ${machine} - Status: ${status}`, "info")
}

// Manipular clique em contato
function handleContactClick(name, phone) {
  if (confirm(`Ligar para ${name}?\n${phone}`)) {
    showNotification(`Ligando para ${name}...`, "success")
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


function updateTimestamps() {
  console.log("Timestamps atualizados")
  
}


function setupKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Ctrl+Q para sair
    if (e.ctrlKey && e.key === "q") {
      e.preventDefault()
      handleExit()
    }

    
    if (e.ctrlKey && e.key === "r") {
      e.preventDefault()
      showNotification("Dashboard atualizado!", "success")
      animateNumbers()
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


function formatTime(minutes) {
  if (minutes < 60) {
    return `${minutes} min`
  } else {
    const hours = Math.floor(minutes / 60)
    return `${hours}h`
  }
}


window.dashboardApp = {
  showNotification,
  animateNumbers,
  handleExit,
}