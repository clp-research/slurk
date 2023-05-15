// https://www.w3schools.com/howto/howto_js_collapsible.asp

let coll = document.getElementsByClassName("collapsible");

for (let i=0; i<coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    let content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
