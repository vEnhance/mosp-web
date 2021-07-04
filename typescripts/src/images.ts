$(() => {
  $('#container img').each(function(_, el) {
    const url = $(el).attr('src')!;
    if (url.indexOf('-sm.') !== -1) {
      const new_url = url.replace('-sm.', '.');
      $("<img />").attr('src', new_url).on('load', () => {
        $(el).attr('src', new_url);
      });
    }
  });
});
