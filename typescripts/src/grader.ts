import SHA from './sha';
import Swal from 'sweetalert2';
import err from './ajaxCrash';

declare const puzzle_slug: string;
declare const hashes: [hash: string];

const audio = new Audio('https://github.com/vEnhance/dotfiles/blob/main/noisemaker/S3-fanfare.mp3?raw=true');
audio.volume = 0.6;

$(function() {
  // Assign relevant metadata
  $('#prize').css('display', 'block');
  let active = false;
  let target_url = '';
  let raw_answer = '';
  let waiting_for_ajax = false;

  function checkAnswer() {
    raw_answer = String($("#answer").val()!);
    $("#answer").val(raw_answer.toUpperCase());
    if (raw_answer && !active) {
      active = true;
      $("#wrong").hide();
      $("#thinking").show();
      $("#percent").css('visibility', 'visible');
      $("#answer").prop('disabled', true);
      guessSalt(0);
    }
  }

  async function guessSalt(t : number) {
    $("#percent").html(t+"%");
    const answer : string = String($("#answer").val()).toUpperCase().replace(/[^A-Z]/g, '');
    for (let i = 111*t; i < 111*(t+1); i++) {
      const g = 'MOSP_LIGHT_NOVEL_' + answer + i;
      const hash = await SHA(g);
      if (hashes.includes(hash)) {
        waiting_for_ajax = true;
        $.post('/ajax', {
          action : 'guess',
          guess : answer,
          salt : i,
          puzzle_slug : puzzle_slug,
        }, (result) => {
          if (!result || !result.correct) {
            err();
          } else if (result.correct == 1) {
            target_url = result.url;
          } else if (result.correct > 0) {
            Swal.fire({
              title : "Stay determined...",
              text : result.message,
              icon : 'success',
            });
          } else {
            err();
          }
          waiting_for_ajax = false;
          judge();
          return;
        }, 'json').fail(err);
      }
    }
    if (t < 100) {
      window.setTimeout(function() { guessSalt(t+1) }, 1);
    } else if (!waiting_for_ajax) {
      judge();
    }
  }

  function judge() {
    $("#thinking").hide();
    if (!target_url) {
      // Incorrect answer
      $("#wrong").show();
      window.setTimeout(function() {
        $("#wrong").css("opacity", "0");
      }, 1000);
      $("#percent").css('visibility', 'hidden');
      $("#answer").prop('disabled', false);
      window.setTimeout(function() {
        $("#wrong").hide();
        $("#wrong").css("opacity", "1");
        active = false;
      }, 4000);
    } else {
      window.setTimeout(() => {
        window.location.replace(target_url);
      }, 8000);
      $("#correct").show();
      $("#back").css('visibility', 'none');
      $("#prize").attr('href', target_url);
      $("#prize").css('z-index', '100');
      $("body").addClass('solved');
      audio.play();
    }
    // If first time solving this puzzle, spend 1 patience and log it on Discord
  }

  $("#answer").val('');
  $("#answer").on('keyup', function(e) {
    if (e.key === "Enter") {
      checkAnswer();
    }
  });
});
