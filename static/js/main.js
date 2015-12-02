$(function() {
  $('input').on('keyup', function() {
    var countem = $(this).val().length;
    $(this).next(".count").text(countem);
  });
});

function monthChanged() {
  var days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  var month = $('.month').val() - 1,
    year = +$('.year').val();
  // Check for leap year if Feb
  if (month === 1 && new Date(year, month, 29).getMonth() === 1) {
    days[1]++;
  }
  $(".day").empty();
  for (var i = $('.day option').length + 1; i <= days[month]; i++) {
    $('<option>').attr('value', i).text(i).appendTo('.day');
  }
}

function checkLeap() {
  var month = $('.month').val() - 1;
  if (month === 1) {
    monthChanged();
  }
}

$(function() {
  monthChanged();
  $('.month').change(monthChanged);
  $('.year').change(checkLeap);
  var currentYear = (new Date).getFullYear();
  $('.year').val(currentYear);
  $('.year').on("click", function() {
    $(this).val("");
  });

  $('.date-input').change(function() {
    $(this).next($('.combined-date')).val($('.month').val() + "/" +
      $(
        '.day option:selected')
      .text() +
      "/" + $('.year').val());
  });

});
