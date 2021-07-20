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
  function checkAnswer() {
    raw_answer = String($("#answer").val()!);
    $("#answer").val(raw_answer.toUpperCase());
    const answer : string = raw_answer.toUpperCase().replace(/[^A-Z]/g, '');
    if (answer && !active) {
      active = true;
      $("#wrong").hide();
      $("#thinking").show();
      $("#percent").css('visibility', 'visible');
      $("#answer").prop('disabled', true);
      guessSalt(0, answer);
    }
  }

  async function guessSalt(t : number, answer : string) {
    $("#percent").html(t+"%");
    for (let i = 111*t; i < 111*(t+1); i++) {
      const g = 'MOSP_LIGHT_NOVEL_' + answer + i;
      const hash = await SHA(g);
      if (i == 2498) {
        console.log(g);
        console.log(hash);
      }
      if (hashes.includes(hash)) {
        $.post('/ajax', {
          action : 'guess',
          guess : answer,
          salt : i,
          puzzle_slug : puzzle_slug,
        }, (result) => {
          if (!result || !result.correct) {
            err();
            return;
          }
          if (result.correct == 1) {
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
        }, 'json').fail(err);
      }
    }
    if (t < 100) {
      window.setTimeout(function() { guessSalt(t+1, answer) }, 1);
    }
    else {
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
