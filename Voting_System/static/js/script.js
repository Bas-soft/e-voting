// change navbar style on scroll

window.addEventListener('scroll', ()=>{
    document.querySelector('nav').classList.toggle
    ('window-scroll',window.scrollY>0)
})

window.addEventListener('scroll', function(){
    var section=document.querySelector('.service');
    var position = section.getBoundingClientRect().top;

    if (position > window.innerHeight){
        section.classList.add('animate');
    }
})



// show/hide calendar answers

function toggleCalendar() {
  var calendar = document.querySelector('.calendar');
  calendar.classList.toggle('visible');
}
// close btn-----------------------


document.addEventListener('DOMContentLoaded', function() {
  var myDiv = document.getElementById('fade_away');
  var closeButton = document.getElementById('close-btn');

  closeButton.addEventListener('click', function() {
    myDiv.style.display = 'none'; // Hide the div
    // Alternatively, you can use CSS classes to control the visibility:
    // myDiv.classList.add('hidden'); // Add a class to hide the div
    // myDiv.classList.remove('hidden'); // Remove the class to show the div
  });
});
 //-------handle pop ups---------------
document.getElementById("openModalLink").addEventListener("click", function() {
  document.getElementById("myModal").style.display = "block";
});

document.getElementsByClassName("close")[0].addEventListener("click", function() {
  document.getElementById("myModal").style.display = "none";
});

 //-------handle staff details pop ups---------------
document.getElementById("view_details").addEventListener("click", function() {
  document.getElementById("myModal_details").style.display = "block";
});

document.getElementsByClassName("close")[0].addEventListener("click", function() {
  document.getElementById("myModal_details").style.display = "none";
});




