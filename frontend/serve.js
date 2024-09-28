const server = Bun.serve({
  static: {
    // health-check endpoint
    "/api/health-check": new Response("All good!"),

    // serve static text
    "/": new Response(await Bun.file("./index.html").bytes(), {
      headers: {
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*", // Enable CORS
      },
    })
  },
  fetch(req) {
    return new Response("404!");
  },
});



console.log(`Listening on ${server.url}`);
