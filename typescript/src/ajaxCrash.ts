import Swal from 'sweetalert2';

export default function err() => {
  Swal.fire({
    title : "Something went wrong",
    text : "Please contact Evan so we can debug this issue",
    icon : 'error',
  });
  return;
}

$(() => {
 $(document).ajaxError(err);
});
