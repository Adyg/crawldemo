var review_page = 1;
$(document).ready(function(){
    $('.more-reviews').click(function(e){
        e.preventDefault();
        var $this = $(this);
        $this.html('Retrieving...');
        $.ajax({
            method: "GET",
            url: '/reviews/'+pid+'/'+review_page,
            cache: false,
            dataType: 'html'
        }).done(function(data){
            $('.reviews-wrap').append(data);
            $this.html('Click here to retrieve more reviews');
            review_page = review_page + 1;
        });        
    });
});
