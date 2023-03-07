import Swal from "sweetalert2";

declare var solver_name: string;

function setName(name: string) {
  $.post(
    "/ajax",
    {
      action: "set_name",
      name: name,
    },
    (result) => {
      if (result.success == 1) {
        $("#tokenname").html(name);
      }
    }
  );
}

function getName() {
  Swal.fire({
    title: "Hello hello hey",
    text: "What should I call you?",
    input: "text",
    icon: "info",
    confirmButtonText: "Set name",
  }).then((result) => {
    if (result.isConfirmed) {
      setName(result.value);
    }
  });
}

$(() => {
  $(".name").html(solver_name);
  $("#setname").on("click", () => {
    getName();
  });
});
