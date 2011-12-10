function checkDate(element) {
   if (element.value == '') {
     // No input;
     feedback = '';
   }
   else {
     var date = new Date(element.value);
     var today = new Date();
     time_delta = date - today;
     date_min = new Date(date.getTime() - time_delta / 2);
     date_max = new Date(date.getTime() + time_delta / 2);
     if (isNaN(date.getTime())) {
       // What did you do, user?
       feedback = 'Invalid date.';
       text_color = 'red';
     }
     else if (time_delta < 1209600000) {
       // Less than 2 weeks or ill-formated.
       feedback = 'Specified date too early. ';
       feedback += 'Choose a date at least two weeks from now.';
       text_color = 'red';
     }
     else {
       feedback = 'Your lightray will return between ';
       feedback += date_min.toDateString();
       feedback += ' and ';
       feedback += date_max.toDateString();
       feedback += '.';
       text_color = 'black';
     }
     document.getElementById("date_feedback").style.color = text_color;
     document.getElementById("date_feedback").innerHTML = feedback;
  }
}
