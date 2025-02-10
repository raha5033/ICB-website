/*-----------------------------------------------------------------------------------

    Template Name: Ibadah - Islamic Center & Mosque HTML Template


    Note: This is Custom Js file

-----------------------------------------------------------------------------------

    [Table of contents]

      01. slider-home-1
      02. slider-ayat
      03. pdf-slider
      04. audio-ayat
      05. mobile-nav
      06. search-box
      07. progressbar
      08. days
      09. accordion-item
      10. scrollTop
  
-----------------------------------------------------------------------------------*/

jQuery(document).ready(function($){
/***--------  01. slider-home-1   ------- ***/
    if ( $.isFunction($.fn.owlCarousel) ) {
    $('.slider-home-1').owlCarousel({
        loop:true,
        arrows:false,
        autoplay:true,
        autoplayTimeout:4000,
        items:1
      })
/***--------  02. slider-ayat   ------- ***/
    $('.slider-ayat').owlCarousel({
        loop:true,
        arrows:false,
        autoplay:true,
        autoplayTimeout:4000,
        items:1
      })
/***--------  03. pdf-slider   ------- ***/
    $('.pdf-slider').owlCarousel({
      loop:true,
      dot:true,
      nav:false,
      autoplay:true,
      autoplayTimeout:3000,
      responsive:{
          0:{
              items:1
          },
          800:{
              items:2
          },
          1200:{
              items:3
          }
        }
      })
/***--------  04. audio-ayat   ------- ***/
    $('.audio-ayat').owlCarousel({
      loop:true,
      nav:true,
      autoplay:true,
      navText: ["<i class='fa-solid fa-angles-left'></i>","<i class='fa-solid fa-angles-right'></i>"],
      responsive:{
          0:{
              items:1
          },
          800:{
              items:2
          },
          1200:{
              items:2
          }
        }
      })
    }

/***--------  05. mobile-nav   ------- ***/
    jQuery('.mobile-nav .menu-item-has-children').on('click', function(e) {
      if ( jQuery( this ).hasClass('active') ) {
            jQuery(this).removeClass('active');
          } else {
            jQuery( '.mobile-nav .menu-item-has-children' ).removeClass('active');
            jQuery(this).addClass('active');
          }
        }); 
        jQuery('#nav-icon4').click(function($){
            jQuery('#mobile-nav').toggleClass('open');
        });
        jQuery('#res-cross').click(function($){
           jQuery('#mobile-nav').removeClass('open');
        });
          jQuery('.bar-menu').click(function($){
            jQuery('#mobile-nav').toggleClass('open');
            jQuery('#mobile-nav').toggleClass('hmburger-menu');
            jQuery('#mobile-nav').show();
        });
        jQuery('#res-cross').click(function($){
           jQuery('#mobile-nav').removeClass('open');
        });
}) ;
/***--------  06. search-box   ------- ***/
    if(jQuery('.search-box-outer').length) {
        jQuery('.search-box-outer').on('click', function() {
            jQuery('body').addClass('search-active');
        });
        jQuery('.close-search').on('click', function() {
            jQuery('body').removeClass('search-active');
        });
    }
/***--------  07. progressbar   ------- ***/
  {
    function animateElements() {
      $('.progressbar').each(function () {
        var elementPos = $(this).offset().top;
        var topOfWindow = $(window).scrollTop();
        var percent = $(this).find('.circle').attr('data-percent');
        var percentage = parseInt(percent, 10) / parseInt(100, 10);
        var animate = $(this).data('animate');
        if (elementPos < topOfWindow + $(window).height() - 10 && !animate) {
          $(this).data('animate', true);
          $(this).find('.circle').circleProgress({
            startAngle: -Math.PI / 2,
            value: percent / 100,
            size: 140,
            thickness: 8,
            emptyFill: "rgba(255,255,255, 0)",
            fill: {
              color: '#fbc50b'
            }
          }).on('circle-animation-progress', function (event, progress, stepValue) {
            $(this).find('div').text((stepValue*100).toFixed() + "%");
          }).stop();
        }
      });
    }

    // Show animated elements
    animateElements();
    $(window).scroll(animateElements);
  };

  // 
  function inVisible(element) {
  //Checking if the element is
  //visible in the viewport
  var WindowTop = $(window).scrollTop();
  var WindowBottom = WindowTop + $(window).height();
  var ElementTop = element.offset().top;
  var ElementBottom = ElementTop + element.height();
  //animating the element if it is
  //visible in the viewport
  if ((ElementBottom <= WindowBottom) && ElementTop >= WindowTop)
    animate(element);
}

function animate(element) {
  //Animating the element if not animated before
  if (!element.hasClass('ms-animated')) {
    var maxval = element.data('max');
    var html = element.html();
    element.addClass("ms-animated");
    $({
      countNum: element.html()
    }).animate({
      countNum: maxval
    }, {
      //duration 5 seconds
      duration: 5000,
      easing: 'linear',
      step: function() {
        element.html(Math.floor(this.countNum) + html);
      },
      complete: function() {
        element.html(this.countNum + html);
      }
    });
  }

}

//When the document is ready
$(function() {
  $(window).scroll(function() {
    $("h2[data-max]").each(function() {
      inVisible($(this));
    });
  })
});

/***--------  08. days   ------- ***/

if(jQuery("#days").length){
    (function () {
        const second = 1000,
        minute = second * 60,
        hour = minute * 60,
        day = hour * 24;

        // Get the target date from the hidden span
        const targetDate = document.getElementById("date_countdown").textContent;
        const countDown = new Date(targetDate).getTime();
        
        const x = setInterval(function() {    
            const now = new Date().getTime();
            const distance = countDown - now;

            // Calculate the values
            document.getElementById("days").innerText = Math.floor(distance / (day));
            document.getElementById("hours").innerText = Math.floor((distance % (day)) / (hour));
            document.getElementById("minutes").innerText = Math.floor((distance % (hour)) / (minute));
            document.getElementById("seconds").innerText = Math.floor((distance % (minute)) / second);

            //do something later when date is reached
            if (distance < 0) {
                document.getElementById("countdown").style.display = "none";
                clearInterval(x);
            }
        }, 1000)
    }());
}

/***--------  09. accordion-item   ------- ***/

jQuery('.accordion-item .heading').on('click', function(e) {
    e.preventDefault();
    if(jQuery(this).closest('.accordion-item').hasClass('active')) {
        jQuery('.accordion-item').removeClass('active');
    } else {
        jQuery('.accordion-item').removeClass('active');
        jQuery(this).closest('.accordion-item').addClass('active');
    }
    var $content = $(this).next();
    $content.slideToggle(600);
    jQuery('.accordion-item .content').not($content).slideUp('fast');
});

/****-----------  10. scrollTop -------------****/

function inVisible(element) {
  var WindowTop = $(window).scrollTop();
  var WindowBottom = WindowTop + $(window).height();
  var ElementTop = element.offset().top;
  var ElementBottom = ElementTop + element.height();
  if ((ElementBottom <= WindowBottom) && ElementTop >= WindowTop)
    animate(element);
}

function animate(element) {
  if (!element.hasClass('ms-animated')) {
    var maxval = element.data('max');
    var html = element.html();
    element.addClass("ms-animated");
    $({
      countNum: element.html()
    }).animate({
      countNum: maxval
    }, {
      duration: 5000,
      easing: 'linear',
      step: function() {
        element.html(Math.floor(this.countNum) + html);
      },
      complete: function() {
        element.html(this.countNum + html);
      }
    });
  }

}
$(function() {
  $(window).scroll(function() {
    $("h2[data-max]").each(function() {
      inVisible($(this));
    });
  })
});
 let calcScrollValue = () => {
  let scrollProgress = document.getElementById("progress");
  let progressValue = document.getElementById("progress-value");
  let pos = document.documentElement.scrollTop;
  let calcHeight =
    document.documentElement.scrollHeight -
    document.documentElement.clientHeight;
  let scrollValue = Math.round((pos * 100) / calcHeight);
  if (pos > 100) {
    scrollProgress.style.display = "grid";
  } else {
    scrollProgress.style.display = "none";
  }
  scrollProgress.addEventListener("click", () => {
    document.documentElement.scrollTop = 0;
  });
  scrollProgress.style.background = `conic-gradient(#007d3a ${scrollValue}%, #fff ${scrollValue}%)`;
};

window.onscroll = calcScrollValue;
window.onload = calcScrollValue;

// end

document.addEventListener('DOMContentLoaded', function() {
    const countdowns = document.querySelectorAll('.countdown');
    
    countdowns.forEach(countdown => {
        const eventTime = new Date(countdown.dataset.eventTime).getTime();
        
        const timer = setInterval(function() {
            const now = new Date().getTime();
            const distance = eventTime - now;
            
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            
            if (distance < 0) {
                clearInterval(timer);
                countdown.innerHTML = "<p>Event has started!</p>";
            } else {
                countdown.querySelector('.days').textContent = days;
                countdown.querySelector('.hours').textContent = hours;
                countdown.querySelector('.minutes').textContent = minutes;
                countdown.querySelector('.seconds').textContent = seconds;
            }
        }, 1000);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Initialize TinyMCE
    tinymce.init({
        selector: '#editor',
        plugins: 'lists link image code table',
        toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist outdent indent | link image | code',
        height: 300
    });

    // Get the form
    const form = document.getElementById('createPageForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submitted'); // Debug log
            
            // Get TinyMCE instance
            const editor = tinymce.get('editor');
            if (!editor) {
                console.error('TinyMCE editor not initialized');
                return;
            }

            // Get form values
            const formData = {
                title: document.getElementById('title').value,
                content: editor.getContent(),
                category: document.getElementById('category').value,
                status: document.getElementById('status').value
            };

            console.log('Form data:', formData); // Debug log

            // Send the request
            fetch('/api/v1/admin/pages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                console.log('Response:', response); // Debug log
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', data);
                alert('Page created successfully!');
                window.location.href = '/admin/pages';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error creating page: ' + error.message);
            });
        });
    }
});
