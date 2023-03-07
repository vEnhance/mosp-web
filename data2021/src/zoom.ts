$(() => {
  const ZOOMDIV = "z";
  const EMAILDIV = "email";
  // https://stackoverflow.com/a/20798567/4826845
  function getIndices(arr: Array<number>, val: number): number[] {
    let indexes = [],
      i;
    for (i = 0; i < arr.length; i++) if (arr[i] === val) indexes.push(i + 1);
    return indexes;
  }
  const extraction = [
    8 + 21,
    21,
    17 + 21,
    4 + 21,
    5 + 21,
    10,
    15,
    3,
    12,
    18 + 21,
    9 + 21,
    13,
  ];
  let has_appended_payload = false;
  let finished_zooming = false;
  const places = Array.from({ length: 43 }).map((_) => "?");
  places[0] = "X"; // pretend array is 1-indexed
  places[1] = "L";
  places[21] = "K";
  places[22] = "E";
  places[42] = "F";
  const init_dpr = window.devicePixelRatio;

  document.body.onresize = function () {
    const STARTING = 125;
    const TARGET = 200;
    const zoom = Math.round((window.devicePixelRatio / init_dpr) * 100);
    if (zoom > STARTING && !has_appended_payload) {
      $("#" + EMAILDIV).append(`<div id="${ZOOMDIV}">ZOOM!</div>`);
      let h = ""; // html output string
      for (let r = 0; r < 6; ++r) {
        if (r == 0) {
          h += places[21];
        } else if (r == 3) {
          h += places[42];
        } else {
          h += " ";
        }
        for (let i = 7 * r + 1; i <= 7 * r + 7; ++i) {
          h += " ==> ";
          h += places[i];
        }
        h += "\n";
        h += " ";
        for (let i = 7 * r + 1; i <= 7 * r + 7; ++i) {
          const indices = getIndices(extraction, i);
          if (indices.length > 0) {
            const s = indices.join(",");
            if (s.length <= 2) {
              h += s.padStart(3, " ") + " ".repeat(3);
            } else {
              h += s.padStart(4, " ") + " ".repeat(2);
            }
          } else {
            h += " ".repeat(6);
          }
        }
        h += "\n";
        if (r == 2) {
          h += "\n";
        }
      }
      $("#" + ZOOMDIV).html(h);
      $("#" + ZOOMDIV).css("position", "absolute");
      $("#" + ZOOMDIV).css("top", "60px");
      $("#" + ZOOMDIV).css("font-size", "18pt");
      has_appended_payload = true;
    }
    if (!finished_zooming && zoom > STARTING) {
      let k = (zoom - STARTING) / (TARGET - STARTING);
      if (k < 0) {
        k = 0;
      }
      if (k > 1) {
        k = 1;
      }
      k = Math.sqrt(k);
      $("#" + ZOOMDIV).css("opacity", k);
      $("#invitation").css("opacity", 1 - k);
    }
    if (zoom >= TARGET) {
      finished_zooming = true;
    }
  };
});
