const base_url = "https://poll-app-hpf4.onrender.com";

function checkAuth(){
  if(!localStorage.getItem("user_id")){
    alert("Login required");
    window.location.href="/";
  }
}

function login(){
  const name=document.getElementById("name").value.trim();
  const password=document.getElementById("password").value.trim();

  if(!name||!password){alert("All fields required");return;}

  fetch(base_url+"/login",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({name,password})})
  .then(r=>r.json())
  .then(d=>{
    if(d.error){alert(d.error);return;}
    localStorage.setItem("user_id",d.user_id);
    window.location.href="/dashboard";
  });
}

function signup(){
  const name=document.getElementById("name").value.trim();
  const password=document.getElementById("password").value.trim();

  fetch(base_url+"/signup-user",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({name,password})})
  .then(r=>r.json())
  .then(d=>{
    alert(d.error||d.message);
    if(!d.error) window.location.href="/";
  });
}

function goToPoll(){window.location.href="/poll";}
function goToVote(){window.location.href="/vote-page";}
function goToResult(){window.location.href="/result";}

function createPoll(){
  const purpose=document.getElementById("purpose").value.trim();
  const venue=document.getElementById("venue").value.trim();
  const description=document.getElementById("description").value.trim();

  if(!purpose||!venue||!description){alert("All fields required");return;}

  fetch(base_url+"/create-poll",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({purpose,venue,description})})
  .then(async res => {const data = await res.json(); 
  
  if (!res.ok){alert(data.message);window.location.href="/dashboard";return;}
  alert("Poll created");window.location.href="/dashboard";});
}

let currentPoll=null;

function loadPoll(){
  fetch(base_url+"/active-poll")
  .then(r=>r.json())
  .then(p=>{
    if(!p){alert("No active poll");window.location.href="/dashboard";return;}
    currentPoll=p;
    document.getElementById("poll-title").innerHTML=p.purpose;
    document.getElementById("poll-desc").innerHTML=p.description;
  });
}

function vote(type){
  let reason="";
  if(type==="no"){
    reason=prompt("Reason?");
    if(!reason){alert("Required");return;}
  }

  fetch(base_url+"/vote",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({
    poll_id:currentPoll.id,
    user_id:localStorage.getItem("user_id"),
    response:type,
    reason
  })})
  .then(r=>r.json())
  .then(d=>{
    if(d.error){alert(d.error);return;}
    alert("Vote done");
    window.location.href="/dashboard";
  });
}
