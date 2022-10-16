container = $("#widget-container");

function displayWidget(activeWidget, isHost=false) {
    switch (activeWidget.widget_type) {
        case "text":
            e = $("<h2>")
                .attr("class", "main-center-card card")
                .append(activeWidget.contents);
            break;
        case "image":
            e = $("<img>")
            .attr("class", "main-center-card card")
                .attr("src", activeWidget.contents);
            break;
        case "text_input":
            e = $("<div>")
                .append(
                    $("<h2>")
                        .attr("class", "main-center-card card")
                        .append(activeWidget.contents.prompt)
                )
            if (!isHost) {
                e.append($("<br>"))
                .append(
                    $("<form>").attr("action", "")
                        .append("<input>")
                            .attr("type", "text")
                            .attr("name", "response")
                    )
                .append("<input>").attr("type", "submit")
            }
            break;
        case "choice":
            e = $("<div>")
                .append(
                    $("<h2>")
                    .attr("class", "main-center-card card")
                    .append(activeWidget.contents)
                )
                .append($("<br>"))
            d = $("<div>").attr("class", "btn-group")
            if (!isHost) {
                d.append($("<br>"));
                allChoices = activeWidget.choices
                for (choice of allChoices) {
                    e.append(
                        $("<button>")
                            .attr("class", "btn")
                            .attr("onclick", `submitAnswer("${choice}")`)
                            .append(choice)
                    );
                }
            }
            e.append(d);
            break;
        default:
            e = $("<h2>")
                .attr("class", "main-center-card card")
                .append(
                    "ERROR: Unknown widget type " + activeWidget.widget_type
                );
            break;
    }
    container.empty().append(e);
}

// $(document).ready(updateWidget);