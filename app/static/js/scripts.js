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

  $(function() {
    $('.ignore-movie').click(function(e) {
      e.preventDefault();
      movieId = $(this).data("movie-id");
      $.post("/ignore_movie/" + movieId);
      $(this).closest('tr').remove();
    })
  })
});
