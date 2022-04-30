declare var require: any;

require.config({
  paths : {
    "sweetalert2" : "https://cdn.jsdelivr.net/npm/sweetalert2@11.0.17/dist/sweetalert2.all.min",
    "jquery" : "https://code.jquery.com/jquery-3.5.1.min",
  }
});

require([
  "sweetalert2",
  "sha",
  "images",
  "grader"
]);
