document.addEventListener('DOMContentLoaded', function() {
  tinymce.init({
    selector: 'textarea.tinymce',
    height: 400,
    menubar: true,
    plugins: [
      'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
      'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
      'insertdatetime', 'media', 'table', 'code', 'help', 'wordcount', 'codesample'
    ],
    toolbar: 'undo redo | blocks | ' +
      'bold italic backcolor | alignleft aligncenter ' +
      'alignright alignjustify | bullist numlist outdent indent | ' +
      'removeformat | help | codesample | image link table | fullscreen',
    content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, San Francisco, Segoe UI, Roboto, Helvetica Neue, sans-serif; font-size: 14px; }',
    skin: 'oxide-dark',
    content_css: 'dark',
    promotion: false,
    branding: false,
    setup: function(editor) {
      // Add a listener to update the hidden textarea before form submission
      editor.on('change', function() {
        editor.save();
      });
    }
  });
  
  // Add form submit handler to ensure content is updated
  document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function() {
      // Save content from all editors to their respective textarea elements
      tinymce.triggerSave();
    });
  });
});