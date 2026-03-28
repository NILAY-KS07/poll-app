self.addEventListener('push', function(event) {
  if (event.data) {
    let payload;
    try {
      payload = event.data.json();
    } catch (e) {
      console.warn("Push message was not valid JSON, treating as plain text:", e);
      payload = {
        title: "Notification", 
        body: event.data.text()
      };
    }

    const options = {
      body: payload.body,
      icon: 'https://cdn-icons-png.flaticon.com/512/5968/5968756.png', 
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: '2'
      }
    };
    event.waitUntil(
      self.registration.showNotification(payload.title, options)
    );
  }
});
