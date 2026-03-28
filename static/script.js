const base_url = "https://poll-app-hpf4.onrender.com";

function checkAuth(){
  if(!localStorage.getItem("user_id")){
    alert("Login required");
    window.location.href="/";
  }
}

// ---------- AUTH ----------

function login(){
  const name=document.getElementById("name").value.trim();
  const password=document.getElementById("password").value.trim();

  if(!name||!password){alert("All fields required");return;}

  fetch(base_url+"/login",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({name,password})
  })
  .then(r=>r.json())
  .then(d=>{
    if(d.error){alert(d.error);return;}
    localStorage.setItem("user_id",d.user_id);
    window.location.href="/dashboard";
  })
  .catch(()=>alert("Server error"));
}

function signup(){
  const name=document.getElementById("name").value.trim();
  const password=document.getElementById("password").value.trim();

  fetch(base_url+"/signup-user",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({name,password})
  })
  .then(r=>r.json())
  .then(d=>{
    alert(d.error||d.message);
    if(!d.error) window.location.href="/";
  })
  .catch(()=>alert("Server error"));
}

// ---------- NAV ----------

function goToPoll(){window.location.href="/poll";}
function goToVote(){window.location.href="/vote-page";}
function goToResult(){window.location.href="/result";}

// ---------- CREATE POLL ----------

function createPoll(){
  const purpose=document.getElementById("purpose").value.trim();
  const venue=document.getElementById("venue").value.trim();
  const description=document.getElementById("description").value.trim();

  if(!purpose||!venue||!description){
    alert("All fields required");
    return;
  }

  fetch(base_url+"/create-poll",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({purpose,venue,description})
  })
  .then(async res=>{
    const data = await res.json();

    if(!res.ok){
      alert(data.message || "Error");
      window.location.href="/dashboard";
      return;
    }

    alert("Poll created");
    window.location.href="/dashboard";
  })
  .catch(()=>alert("Server error"));
}

// ---------- LOAD ACTIVE POLL ----------

let currentPoll=null;

function loadPoll(){
  fetch(base_url+"/active-poll")
  .then(r=>r.json())
  .then(p=>{
    
    if(!p || !p.id){
      alert("No active poll");
      window.location.href="/dashboard";
      return;
    }

    currentPoll=p;

    document.getElementById("poll-title").innerHTML=p.purpose;
    document.getElementById("poll-desc").innerHTML=p.description;
  })
  .catch(()=>alert("Server error"));
}

// ---------- VOTE ----------

function vote(type){
  let reason="";

  if(type==="no"){
    reason=prompt("Reason?");
    if(!reason){
      alert("Required");
      return;
    }
  }

  fetch(base_url+"/vote",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      poll_id:currentPoll.id,
      user_id:localStorage.getItem("user_id"),
      response:type,
      reason
    })
  })
  .then(r=>r.json())
  .then(d=>{
    if(d.error){
      alert(d.error);
      return;
    }

    alert("Vote done");
    window.location.href="/dashboard";
  })
  .catch(()=>alert("Server error"));
}



function loadResults(){
  fetch(base_url+"/active-poll")
  .then(r=>r.json())
  .then(p=>{
    if(!p || !p.id){
      alert("No active poll");
      return;
    }

    fetch(base_url+"/results/"+p.id)
    .then(r=>r.json())
    .then(data=>{
      const container=document.getElementById("results");
      container.innerHTML="";

      data.forEach(v=>{
        const div=document.createElement("div");

        
        div.innerHTML = `
          <p><strong>${v.name}</strong> voted: ${v.response}</p>
          <p>${v.reason ? "Reason: "+v.reason : ""}</p>
          <hr>
        `;

        container.appendChild(div);
      });
    });
  })
  .catch(()=>alert("Server error"));
}
function initNotifications(){
  Notification.requestPermission().then(permission=>{
    if(permission==="granted"){
      messaging.getToken({ vapidKey: "YOUR_VAPID_KEY" })
      .then(token=>{
        console.log("TOKEN:", token);

        fetch(base_url+"/save-token",{
          method:"POST",
          headers:{"Content-Type":"application/json"},
          body:JSON.stringify({
            user_id: localStorage.getItem("user_id"),
            token: token
          })
        });
      })
      .catch(err=>{
        console.log("Token error:", err);
      });
    }
  });
}
