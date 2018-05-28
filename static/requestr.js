function Client(data) {
    this.name = ko.observable(data.name)
}

function Request(data) {
    var self = this;

    self.id = ko.observable(data.id);
    self.title = ko.observable(data.title);
    self.description = ko.observable(data.description);
    self.target = ko.observable(data.target);
    self.area = ko.observable(data.area);
    self.client = ko.observable(data.client);
    self.priority = ko.observable(data.priority);

    // Issues a delete instruction to backend for a request
    self.delete = function(r) {
        return $.ajax({
            url: '/requests/delete',
            contentType: 'application/json',
            type: 'POST',
            data: JSON.stringify({
                'id': self.id(),
            }),
            success: function(data) {
                console.log('Request deleted');
                return true;
            },
            error: function() {
                console.log('Failed to delete request');
                return false;
            }
        });
    };
}

function RequestListViewModel() {
    var self = this;
    self.clients = ko.observableArray([]);
    self.requests = ko.observableArray([]);

    // Loads requests from backend into self.requests
    self.loadRequests = function() {
        $.getJSON('/requests', function(requestModels) {
        	var r = $.map(requestModels.requests, function(item) {
        	    return new Request(item);
        	});
        	self.requests(r)
        });
    }
    self.loadRequests();

    // Loads clients from backend into self.clients
    $.getJSON('/clients', function(clientModels) {
    	var r = $.map(clientModels.clients, function(item) {
    	    return new Client(item);
    	});
    	self.clients(r);
    });

    // Retains sorting of requests in front end. Default sort is Priority then Client.
    self.sortedRequests = ko.computed(function() {
        return self.requests().sort(function(a, b) {
            return a.priority() - b.priority() || a.client().localeCompare(b.client());
        });
    });

    self.newTitle = ko.observable();
    self.newDescription = ko.observable();
    self.newTarget = ko.observable();
    self.newArea = ko.observable();
    self.newClient = ko.observable();
    self.newPriority = ko.observable();

    // Adds a request in the backend, then clears form inputs
    self.addRequest = function() {
    	self.save();

    	self.newTitle("");
    	self.newDescription("");
    	self.newTarget("");
    	self.newPriority("");
    };

    // Tries to delete a request in the backend, if successful removes request
    // from the array
    self.deleteRequest = function(request) {
        d = request.delete()

        if (d) {
            self.requests.remove(request);
        }
    };

    // Saves a new request in the backend. On success, reloads the requests array.
    self.save = function() {
    	return $.ajax({
    	    url: '/requests/new',
    	    contentType: 'application/json',
    	    type: 'POST',
    	    data: JSON.stringify({
        		'title': self.newTitle(),
        		'description': self.newDescription(),
        		'target': self.newTarget(),
        		'area': self.newArea(),
        		'client': self.newClient().name(),
        		'priority': self.newPriority(),
    	    }),
    	    success: function(data) {
        		console.log("Request added, reloading requests array");
                self.loadRequests();
        		return;
    	    },
    	    error: function() {
    	    	return console.log("Failed");
    	    }
    	});
    };
}

ko.applyBindings(new RequestListViewModel());