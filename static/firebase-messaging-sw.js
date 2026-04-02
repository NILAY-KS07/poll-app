self.addEventListener('push', function(event) {
    if (event.data) {
        let payload;
        try {
            payload = event.data.json();
        } catch (e) {
            console.warn("Payload not JSON, using text fallback.");
            payload = { 
                notification: { 
                    title: "Poll Update", 
                    body: event.data.text() 
                } 
            };
        }


        const notification = payload.notification || payload.data || {};
        const title = notification.title || payload.title || "New Poll Live!";
        const body = notification.body || payload.body || "A new poll has started. Tap to vote!";

        const options = {
            body: body,
            icon: 'https://cdn-icons-png.flaticon.com/512/5968/5968756.png', 
            vibrate: [200, 100, 200],
            badge: 'https://cdn-icons-png.flaticon.com/512/5968/5968756.png',
            data: {
                click_action: '/dashboard' // Redirects user when they click
            }
        };

        event.waitUntil(
            self.registration.showNotification(title, options)
        );
    }
});


self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});
