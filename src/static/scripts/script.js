'use strict';

var app = angular.module('jobdex_app', ['ngCookies']);
app.controller('UserController', function($scope, $http) {
	this.user = {};

	this.sign_up = function(){		
		//Modeled off of http://tutorials.jenkov.com/angularjs/ajax.html		
		$http.post(dummyURL.herokuapp.com/UserModel/sign_up, {user: this.user.username, password: this.user.password, email: this.user.email}).
			success(function(data, status headers, config) {
				if (data.errCode <= 0) {
					this.errorHandler(data.errCode);
				}
				else if (data.errCode == 1){
					//add to dummyUsers
					dummyUsers.push(data.user);
					this.user = {};
				}
			}).error(function(data, status headers, config) {
			//add error handling function
		});
	};

	this.login = function(){
		//Modeled off of http://tutorials.jenkov.com/angularjs/ajax.html		
		$http.post('/login.json', {user: this.user.username, password: this.user.password}).
			success(function(data, status headers, config) {
				if (data.errCode <= 0) {
					this.errorHandler(data.errCode);
				}
				else if (data.errCode == 1){
					// sucess
				}
			}).error(function(data, status headers, config) {
			//add error handling function
		});
	};

	this.logout = function(){
		this.user = {};
				
		$http.post('/logout.json', {user: this.user.username, password: this.user.password}).
			success(function(data, status headers, config) {
			//add success result
				if (data.errCode <= 0) {
					this.errorHandler(data.errCode);
				}
				else if (data.errCode == 1){
					// sucess 
				}
			}).error(function(data, status headers, config) {
			//add error handling function
		});

		//Add navigation for HTML
		//Save cookies to the backend
	}

	var ERR_BAD_CREDENTIALS = -1;
	var ERR_EXISTING_USER = -2;
	var ERR_BAD_USERNAME = -3;
	var ERR_BAD_PASSWORD = -4;

	this.errorHandler = function(errCode) {
		if (errCode == ERR_BAD_CREDENTIALS){
			console.log("Bad Credential");
		}
		else if (errCode == ERR_EXISTING_USER){
			console.log("User Exists");
		}
		else if (errCode == ERR_BAD_USERNAME){
			console.log("Bad Username");
		} 
		else if (errCode == ERR_BAD_PASSWORD){
			console.log("BAD_PASSWORD");
		}
	}


});

app.controller('CardController', ['$http', function($http){

	this.add_tag = function(tagName){
		

		$http.post('/add-tags.json', {tagName: tagName}).success(function(data, status headers, config){
			this.tags.push(tagName);
		});

		$http.post('/add-tags.json', {tagName: tagName}).error(function(data, status headers, config){
			//Handle error
		});

	};

	this.modify_tag = function(currentTagName, newTagName){

		this.currentTagIndex = this.tags.indexOf(currentTagName);

		$http.post('/modify-tag.json', {currentTagName: 'currentTagName', newTagName: newTagName}).
			success(function(data, status headers, config){
				this.tags.splice(this.currentTagIndex, 1);
				this.tags.push(tagName);
		}).error(function(data, status headers, config){
			//Handle error
		});

	};

	this.get_tags = function(tagName){


		$http.get('/get-tags.json').success(function(data, status headers, config){
			//LOG??
		}).error(function(data, status headers, config){
			//Handle error
		});

	};

	this.remove_tag = function(cardId, tagName){

		this.tagIndex = this.tags.indexOf(tagName);

		$http.post('/modify-tag.json', {currentTagName: currentTagName, newTagName: newTagName}).
			success(function(data, status headers, config){
				this.tags.splice(this.tagIndex, 1);
			}).error(function(data, status headers, config){
			//Handle error
		});

	};

	this.create_card = function(companyName, jobTitle, status){
	

		$http.post('/create-card.json', {companyName: companyName, jobTitle: jobTitle, status: status}).
			success(function(data, status headers, config){
			
			}).error(function(data, status headers, config){
			//Handle error
		});

	};

	$scope.modify_card_status = function(cardId, updatedStatus){

		$scope.myData = JSON.stringify({card_id: cardId, status: updatedStatus});
		var responsePromise = $http.post(dummyURL.herokuapp.com/CardModel/modify_card_status, $scope.myData);
		
		responsePromise.success(function(data, status, headers, config) {
	};

	$scope.get_user_cards = function(user){
		$scope.myData = JSON.stringify({username: user});
		var responsePromise = $http.get(dummyURL.herokuapp.com/CardModel/get_user_cards. $scope.myData);
	};

}]);

app.controller('DocumentController', function($scope, $http) {
	
	$scope.upload_document = function(user, PDFdoc){
		$scope.myData = JSON.stringify({username: user, PDF: PDFdoc});
		var responsePromise = $http.post(dummyURL.herokuapp.com/DocumentModel/upload_document. $scope.myData);

		responsePromise.success(function(data, status, headers, config) {

		});

		responsePromise.error(function(data, status, headers, config){
		});
	};

	this.remove_document = function(doc_id){
		$http.post('/remove_document.json', {username: user, docId: doc_id}).
			success(function(data, status, headers, config) {
				if (data.errCode <= 0) {
					this.errorHandler(data.errCode);
				}
				else if (data.errCode == 1){
					// sucess
				}
			}).responsePromise.error(function(data, status, headers, config){
		});
	};

	this.get_documents = function(user_id){
		$http.get('/get_documents.json', {userId: user_id}).
			success(function(data, status, headers, config) {
				if (data.errCode <= 0) {
					this.errorHandler(data.errCode);
				}
				else if (data.errCode == 1){
					// sucess
				}
			}).responsePromise.error(function(data, status, headers, config){
		});
	};

	var ERR_DOC_NOTFOUND = -1;
	var ERR_DOC_EXISTS = -2;

	this.errorHandler = function(errCode) {
		if (errCode == ERR_DOC_NOTFOUND){
			console.log("Document Not Found");
		}
		else if (errCode == ERR_DOC_EXISTS){
			console.log("Document Exists");
		}
	}	

});

var dummyUsers = [{
	username: 'seth',
	password: 'hello',
	email: 'sethanderson@berkeley.edu',
	id: 1234
}, {
	username: 'yaxin',
	password: 'goodbye',
	email: 'yaxin.t@berkeley.edu',
	id: 5678
}];

var dummyCards = [{
	companyName: 'Uber',
	jobTitle: 'Software Engineer',
	status: 0,
	tags: [
	'backend',
	'SF',
	'python'
	]
	id: 9999
}, {
	companyName: 'Uber',
	jobTitle: 'Sales Assistant',
	status: 1,
	tags: [
	'client-side',
	'SF',
	'low salary'
	]
	id: 5555
}, {
	companyName: 'Google',
	jobTitle: 'Software Engineer',
	status: 1,
	tags: [
	'frontend',
	'Mountain View',
	'good culture'
	]
	id: 3333
}];

var dummyDocuments = [{
	docName: 'resume_softwareEngineer',
	type: 'pdf',
	url: '',
}, {
	docName: 'resume_salesAssistant',
	type: 'pdf',
	url: '',
}]
