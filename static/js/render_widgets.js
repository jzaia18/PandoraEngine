container = $("#widget-container");

function updateWidget() {
    switch (activeWidget.widget_type) {
        case "text":
            e = $("<p>").append(activeWidget.contents);
            break;
        case "image":
            e = $("<img>").attr("src", activeWidget.contents);
            break;
        case "text_input":
            e = $("<div>")
                .append($("<p>").append(activeWidget.contents.prompt))
                .append($("<br>"))
                .append(
                    $("<form>").attr("action", "")
                        .append("<input>").attr("type", "text").attr("name", "response")
                    )
                .append("<input>").attr("type", "submit")
            break;
        case "choice":
            e = $("<div")
        default:
            e = $("<p>").append(
                "ERROR: Unknown widget type " + activeWidget.widget_type
            );
            break;
    }
    container.empty().append(e);
}

$(document).ready(updateWidget);