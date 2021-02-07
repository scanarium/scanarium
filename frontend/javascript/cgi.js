var cgis = {
  ' ': 'scan',
  'n': 'reset-dynamic-content',
  's': 'show-source',
  'r': 'reindex'
};

var cgiFail = function(uuid, cgi, reason, parameters) {
  var msg = localize('{cgi_name} failed', {'cgi_name': cgi});
  msg += ': ' + localize(reason, parameters);
  MessageManager.addMessage(uuid, 'failed', msg);
};

var onReadyStateChange = function(cgi) {
  return function() {
    if (this.readyState === XMLHttpRequest.DONE) {
      var capsule = {};
      var prefix = '';
      var is_ok = false;
      if (this.status == 200) {
        capsule = JSON.parse(this.responseText);
        is_ok = sanitize_boolean(capsule, 'is_ok');
      } else {
        capsule = {
          'is_ok': false,
          'error_template': 'Response status was {response_status_code} instead of 200',
          'error_parameters': {'response_status_code': this.status.toString()}
        };
      }

      var status = (is_ok ? 'ok' : 'failed')
      prefix = localize('{cgi_name} ' + status, {'cgi_name': cgi});
      CommandProcessor.process(capsule, prefix);
    }
  };
};

