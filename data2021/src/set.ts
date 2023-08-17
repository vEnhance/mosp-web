/*
 * Adapted from the Set with Friends website
 * https://github.com/ekzhang/setwithfriends
 * Written by Eric Zhang and Cynthia Du
 *
 * MIT License
 *
 * Copyright (c) 2020 Eric Zhang, Cynthia Du
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import Swal from "sweetalert2";

export function SetCard(value: string, month: string, day: number): string {
  // dark theme
  const theme = {
    palette: {
      type: "dark",
      primary: {
        light: "#c5cae9",
        main: "#8c9eff",
        dark: "#536dfe",
      },
      secondary: {
        light: "#ff80ac",
        main: "#ff4284",
        dark: "#c51162",
      },
      action: {
        hover: "#363636",
      },
      success: {
        light: "#81c784",
        main: "#a5d6a7",
        dark: "#82c483",
      },
      background: {
        panel: "#303030",
        paper: "#262626",
        default: "#161616",
      },
    },
    input: {
      textColor: "#fff",
      caretColor: "#fff",
      background: "#262626",
    },
    pie: {
      noGames: "#rgba(0, 0, 0, 0.12)",
    },
    setCard: {
      purple: "#ff47ff",
      green: "#00b803",
      red: "#ffb047",
      background: "#404040",
    },
    profileTable: {
      row: "#282828",
    },
    setFoundEntry: "rgba(130, 170, 100, 0.15)",
  };

  const SHAPES = ["squiggle", "oval", "diamond"];
  const SHADES = ["filled", "outline", "striped"];

  function Symbol(
    arg_color: number,
    arg_shape: number,
    arg_shade: number,
  ): string {
    const COLORS = [
      theme.setCard.purple,
      theme.setCard.green,
      theme.setCard.red,
    ];

    const color = COLORS[arg_color];
    const shape = SHAPES[arg_shape];
    const shade = SHADES[arg_shade];
    const width = 18;
    const height = 36;
    const fill = shade === "outline" ? "transparent" : color;
    const mask = shade === "striped" ? "url(#mask-stripe)" : "";
    return `<svg
        class="symbol"
        width="${width}"
        height="${height}"
        viewBox="0 0 200 400"
      >
        <use
          xlink:href="${"#" + shape}"
          fill="${fill}"
          mask="${mask}"
        />
        <use xlink:href="${"#" + shape}"
          stroke="${color}" fill="none" stroke-width="12px" />
      </svg>`;
  }

  // 4-character string of 0..2
  const color = value.charCodeAt(0) - 48;
  const shape = value.charCodeAt(1) - 48;
  const shade = value.charCodeAt(2) - 48;
  const number = value.charCodeAt(3) - 48;
  const symbols = [...Array(number + 1)]
    .map(() => Symbol(color, shape, shade))
    .join("\n");

  return `<div class="card fresh" data-vector="${value}" data-day="${day}">
    ${symbols}\n
    <span class="tooltip">${month} ${day}</span>
    </div>`;
}

const progress: number[][] = JSON.parse(
  localStorage.getItem("setClicks") || "[[],[],[],[],[],[],[],[],[],[],[]]",
);

const initialized: boolean[] = Array(10).fill(false);

let current_board = 0;

// Startup
export function createEmptyBoards() {
  const FAKE_CARD = `<div class="card fake"><svg class="symbol" width="18" height="36" viewBox="0 0 200 400"></svg></div>`;
  $("#puzzlecontent").append(
    `<div id="taskselect">&bullet; </div>` +
      `<h2 id="boardtitle"></h2>` +
      `<div id="boards"></div>`,
  );
  $("#taskselect").css("text-align", "center");

  // Set up the boards
  for (let i = 0; i < 10; ++i) {
    const month = i == 2 ? "September" : "July";
    $("#taskselect").append(
      `<a href="#${i + 1}" id="${i + 1}">#` + (i + 1) + `</a> &bullet; `,
    );
    $("#boards").append(`<div id="board${i}" class="board"></div>`);
    // Trigger when board link is clicked
    $(`#${i + 1}`).on("click", () => {
      current_board = i;
      $("div.board").hide().removeClass("showing");
      $(`#board${i}`).show().addClass("showing");
      $("#boardtitle").html(`Calendar ${i + 1} (${month})`);
      if (!initialized[i]) {
        initialized[i] = true;
        let j = 0; // time delay
        for (const x of progress[i]) {
          j++;
          window.setTimeout(
            () => {
              $(`#board${i} > div.card[data-day=${x}]`).trigger("click");
            },
            100 + Math.round(300 * Math.pow(j, 0.6)),
          );
        }
      }
    });
  }

  // Shift and reset button
  $("#taskselect").append(
    `<p>&bullet; ` +
      `<a href="javascript:void(0)" id="shift">Shift</a>` +
      ` &bullet; ` +
      `<a href="javascript:void(0)" id="reset">Reset progress</a>` +
      ` &bullet;</p>`,
  );
  $("#shift").on("click ", function () {
    $("div.board.showing").prepend(FAKE_CARD);
    const fakes = $("div.board.showing > div.card.fake");
    if (fakes.length >= 7) {
      fakes.remove();
    }
    $("div.board.showing > div.card.gotten").each(function () {
      const is_ok = Number($(this).attr("data-break")) != fakes.length % 7;
      $(this).toggleClass("ok", is_ok);
      $(this).toggleClass("bad", !is_ok);
    });
  });
  $("#reset").on("click ", function () {
    Swal.fire({
      title: "Are you sure?",
      text: "This erases all your hard work identifying SET's.",
      icon: "warning",
      confirmButtonText: "Reset SET progress.",
      cancelButtonText: "Abort!",
      showCancelButton: true,
      reverseButtons: true,
    }).then((result: any) => {
      if (result.isConfirmed) {
        localStorage.removeItem("setClicks");
        self.location.reload();
      }
    });
  });
}

/* Set up the clicks and set checker */
export function finishSetup() {
  $("div.card.fresh").on("click", function () {
    if ($(this).hasClass("fresh")) {
      $(this).toggleClass("selected");
      const selected = $("div.board.showing > div.card.fresh.selected");

      // Check if they form a tromino set
      if (selected.length <= 2) {
        return;
      } else if (selected.length >= 4) {
        selected.removeClass("selected");
        $(this).addClass("selected");
        return;
      }

      // Get the of the cards indices
      const A = selected.eq(0);
      const B = selected.eq(1);
      const C = selected.eq(2);
      const a = Number(A.attr("data-day"));
      const b = Number(B.attr("data-day"));
      const c = Number(C.attr("data-day"));
      const differences = [Math.abs(a - b), Math.abs(b - c), Math.abs(c - a)];
      if (!differences.includes(1)) return;
      if (!differences.includes(7)) return;
      const u = A.attr("data-vector")!;
      const v = B.attr("data-vector")!;
      const w = C.attr("data-vector")!;
      for (let i = 0; i < 4; ++i) {
        if (
          (Number(u.slice(i, i + 1)) +
            Number(v.slice(i, i + 1)) +
            Number(w.slice(i, i + 1))) %
            3 !=
          0
        ) {
          return;
        }
      }

      // this is a valid Set, let's store it for future reference
      function addToProgress(n: number) {
        if (!progress[current_board].includes(n)) {
          progress[current_board].push(n);
        }
      }
      addToProgress(Number(A.attr("data-day")));
      addToProgress(Number(B.attr("data-day")));
      addToProgress(Number(C.attr("data-day")));
      localStorage.setItem("setClicks", JSON.stringify(progress));

      // get the bad offset thing
      const x = Math.min(a % 7, b % 7, c % 7);
      const y = Math.max(a % 7, b % 7, c % 7);
      const breakpoint = x == 0 && y == 6 ? 1 : (7 - x) % 7;

      const fakes = $("div.board.showing > div.card.fake");
      const offset = fakes.length;

      const now = Date.now();
      selected.each(function () {
        $(this).removeClass("selected");
        $(this).removeClass("fresh");
        $(this).addClass(breakpoint != offset ? "gotten ok" : "gotten bad");
        $(this).attr("data-break", breakpoint);
        $(this).attr("data-when", now);
      });
      const gotten = $("div.board.showing > div.card.gotten");
      if (gotten.length == 24) {
        const leftover = $("div.board.showing > div.card.fresh");
        leftover.removeClass("fresh");
      }
    }
  });
  function getFriends(el: JQuery) {
    if ($(el).hasClass("gotten")) {
      const when = $(el).attr("data-when");
      return $(`div.board.showing > div.card.gotten[data-when=${when}]`);
    } else {
      return $(); // none
    }
  }
  $("div.card.fresh").on("mouseenter", function (this: HTMLElement) {
    getFriends($(this)).addClass("highlight");
  });
  $("div.card.fresh").on("mouseleave", function (this: HTMLElement) {
    getFriends($(this)).removeClass("highlight");
  });
  $("div.board").hide();
  if (window.location.hash) {
    $(window.location.hash).trigger("click");
    $(window.location.hash)[0].scrollIntoView(true);
  }
}
