$(function(){
    $("body").on('click', '.report', function() {
        $(this).toggleClass('collapsed');
        return false;
    });

    
    function updateRepo(button) {
        var id = $(button).parents(".repository").attr("data-id");
        $.get("repopart/"+id, function(data) { 
            $(button).parents(".repository").replaceWith(data);
        });
    }
    
    function checkStatus(id, l) {
        $.get("taskstatus/"+id, function(data) {
            if(data=="False") {
              $(l).text($(l).text()+'.');
              setTimeout(function(){checkStatus(id, l);}, 800);
            } else {
              $(l).text($(l).text() + " Done, please wait for results.");
              $(l).parents(".repository").removeClass("running");
              //$(l).removeClass("runningb");
              // just enough time to see the result
              setTimeout(function(){updateRepo(l);}, 2000);
              
            }
        });
    }
    
    $("body").on("click", ".launch", function(e) {
      e.preventDefault();
      var l = this;
      var repo = $(this).parents(".repository")
      if($(this).hasClass("runningb")) {
        return false;
      }
      $(this).addClass("runningb");

      repo.addClass("running");
      var force = repo.find(".force")[0].checked;
      $.get(l.href+"?force="+force, function(data) {
        $(l).text("Running ");
        checkStatus(data, l);
      });
      
      return false;
    });
});