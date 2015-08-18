$(document).ready(function() {
  $(function() {
    $('.rate-movie').barrating({
      theme: 'bootstrap-stars',
      onSelect: function(value, text) {
        movieId = $(this).closest(".movie-rating").data("movie-id");
        console.log('Selected rating: ' + value + " " + movieId);
        if (value == "") {
          value = 0;
        }
        $.post("/rate_movie/" + movieId + "/" + value);
      }
    });
  });
});
