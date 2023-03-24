<script type="text/javascript">
$(document).ready(function(){
    $("#bing").load("https://raw.githubusercontent.com/meisnate12/PMM-Image-Sets/master/movies/readme.md", function () {
        $(".image-accordion").click(function () {
            this.classList.toggle("image-active");
            var parent = this.parentElement;
            var panel = this.nextElementSibling;
            if (panel.style.maxHeight) {
                panel.style.maxHeight = null;
            } else {
                panel.style.maxHeight = parseInt(panel.scrollHeight) + 10 + "px";
                parent.style.maxHeight = parseInt(parent.style.maxHeight) + panel.scrollHeight + "px";
            } 
            if (panel.style.paddingBottom) {
                panel.style.paddingBottom = null;
            } else {
                panel.style.paddingBottom = "10px";
            } 
        });
    });
});
</script>

<div id="bing"></div>