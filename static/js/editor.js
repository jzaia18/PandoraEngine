// List 1
$('#widgets').sortable({
    group: {
        name: 'shared',
        pull: 'clone', // To clone: set pull to 'clone'
	put: false
    },
    animation: 200,
    ghostClass: 'ghost',
    handle: '.handle',
    sort: false
});

// List 2
$('#timeline').sortable({
    group: 'shared',
    animation: 200,
    ghostClass: 'ghost',
    handle: '.handle',
    onSort: reportActivity
});

var widget_id = 0;

function post_timeline() {
    let all_widgets = {};
    
    for (elem of $('#timeline')[0].children) {
	var widget = {
	    widget_type: elem.id.split('-')[1],
	    timer: Number($('#timer-' + elem.id)[0].value)
	}

	if (widget.widget_type == 'text') {
	    widget.contents = $('#content-' + elem.id)[0].value
	} else if (widget.widget_type == 'choice') {
	    if (elem.id.includes('rand')) {
		widget.contents = $('#tag-' + elem.id)[0].value;
		widget.random = true;
		widget.choices = null;
	    } else {
		var inputs = $('#answer-choices-' + elem.id + ' li input');
		var choices = [];
		for (input of inputs) {
		    choices.push(input.value);
		}
		widget.contents = $('#prompt-' + elem.id)[0].value;
		widget.random = false;
		widget.choices = JSON.stringify(choices);
	    }
	    widget.opinion = $('#fact-opinion-' + elem.id)[0].checked;
	    widget.timer = $('#timer-' + elem.id)[0].value;
	}
	
	all_widgets[elem.id] = widget;
    }

    console.log(all_widgets);

    var arr = [];

    function recurse_ajax(objs) {
	if (objs.length == 0) {
	    for (key of Object.keys(all_widgets)) {
			all_widgets[key] = JSON.stringify(all_widgets[key])
	    }

	    $.ajax({
		type: "POST",
		url: "/generateWidgets",
		data: all_widgets,
		success: function (data) {
		    console.log('Widgets created!');
			console.log(data);

			var game_data = {
				name: $('#game-name')[0].value,
				max_players: Number($('#game-num-players')[0].value),
				widgets: JSON.stringify(data['widgets'])
			}

			$.ajax({
				type: "POST",
				url: "/addGame",
				data: game_data,
				success: function(e) {
					console.log(e);
					window.location = '/';
				},
				error: function (e) {
					alert(JSON.stringify(e))
				}
			});
		},
		error: function (e) {
		    alert(JSON.stringify(e))
		}
	    });
	}
	else {
	    $.ajax({
		type: "POST",
		url: "/validateWidget",
		data: objs[0],
		success: function (data) {
		    console.log('Widget validated.');
		    console.log(data);
		    recurse_ajax(objs.slice(1));
		},
		error: function (e) {
		    alert(JSON.stringify(e));
		},
	    });
	}
    }

    recurse_ajax(Object.values(all_widgets))
}

$('#submit-game').click(post_timeline);

/* 
function show_hide_div(calling_widget_name) {
    var widget_name = calling_widget_name.split('-').slice(2).join('-');
    console.log("#answers-" + widget_name);
    if ($("#answers-" + widget_name)[0].style.visibility == '') {
	$("#answers-" + widget_name)[0].style.visibility = 'hidden';
    }
    else {
	$("#answers-" + widget_name)[0].style.visibility = '';
    }
}
*/

function createChoiceOption(widget_id) {
    return '<li><input type="text" placeholder="Enter answer choice here" /></li>';
}

function addChoice(widget_id) {
    widget_id = widget_id.split('-').slice(1).join('-')
    $("#" + widget_id)[0].append($(createChoiceOption())[0]);
}

function create_widget_info(widget_type, widget_id) {
    var widget_name = 'widget-' + widget_type + '-' +  widget_id;
    var content = '<div id="form-' + widget_name + '">';
    content += '<label for="timer-' + widget_name + '">Time (s):</label>';
    content += '<input id="timer-' + widget_name + '" type="number" value=30 min=0 max=999 /><br />';
    
    if (widget_type=='text') {
	content += '<label for="content-' + widget_name + '">Display Text:</label>';
	content += '<textarea id="content-' + widget_name + '"></textarea>';
    }
    else if (widget_type.includes('choice')) {
	content += '<label for="fact-opinion-' + widget_name + '">Opinion Question?</label>';
	content += '<input type="checkbox" id="fact-opinion-' + widget_name + '" />';
	//content += onChange="show_hide_div(this.id)"

	if (widget_type.includes('rand')) {
	    content += '<label for="tag-' + widget_name + '">Question Tags (space separated):</label>';
	    content += '<input type="text" id="tag-' + widget_name + '" />';
	}
	else {
	    content += '<label for="prompt-' + widget_name + '">Question:</label>';
	    content += '<input type="text" id="prompt-' + widget_name + '" />';

	    content += '<div id="answers-' + widget_name + '">';
	    content += '<p>Enter the possible answer choices, the 1st is the correct answer (if not an opinion game)</p>';
	    content += '<ul id="answer-choices-' + widget_name + '">'
	    content += createChoiceOption();
            content += '</ul>';
	    content += '<button id="add-answer-choices-' + widget_name + '"class="btn-primary btn" onclick="addChoice(this.id)">Add choice</button>'
	    content += '</div>';
	}
    }

    content += '</div>';
    return content
}

function removeItem(widget) {
	$('#' + widget).remove();
}

// Report when the sort order has changed
function reportActivity(e) {
    if (e.pullMode == 'clone') {
	//console.log(e);
	var widget_type = e.item.id.split('-').slice(1).join('-');
	e.item.id += '-' + widget_id;

	var widget_controls = create_widget_info(widget_type, widget_id);
	widget_id++;

	$('#' + e.item.id).append($('<button class="btn btn-primary widget-drop-control" type="button" data-bs-toggle="collapse" data-bs-target="#options-' + e.item.id + '" aria-expanded="false" aria-controls="options-' + e.item.id + '"> \
		  Info \
	      </button> \
	      <div class="collapse" id="options-' + e.item.id + '"> \
		  <div class="card card-body"> \
		  ' + widget_controls + '\
		  </div> \
		  <button onclick="removeItem(\'' + e.item.id + '\')">Remove</button>\
	      </div>'));
    }
};
