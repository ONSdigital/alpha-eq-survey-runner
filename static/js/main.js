$(function() {
  $('input').on('keyup', function() {
    var countem = $(this).val().length;
    $(this).next(".count").text(countem);
  });
});
