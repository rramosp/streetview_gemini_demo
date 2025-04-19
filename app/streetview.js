function initialize() {
  const fenway = { lat: 42.345573, lng: -71.098326 };
  const map = new google.maps.Map(document.getElementById("map"), {
    center: fenway,
    zoom: 14,
  });
  const panorama = new google.maps.StreetViewPanorama(
    document.getElementById("pano"),
    {
      position: fenway,
      pov: {
        heading: 345,
        pitch: 10,
      },
    },
  );

  map.setStreetView(panorama);
  document.panorama = panorama
  document.map = map
}

async function call_gemini() {
  var panorama = document.panorama
  const position = panorama.getPosition();
  const pov = panorama.getPov();
  const zoom = panorama.getZoom();

  console.log("LatLng:", position.lat(), position.lng());
  console.log("Heading:", pov.heading);
  console.log("Pitch:", pov.pitch);
  console.log("Zoom:", zoom);

  var p = document.getElementById('prompt').value
  var request_body = JSON.stringify({
    prompt: p,
    lat: position.lat(),
    lon: position.lng(),
    pitch: pov.pitch,
    heading:  pov.heading,
    zoom: zoom
  })
  
  document.getElementById('ask-gemini-button').classList.add("disabled");
  document.getElementById('prompt').classList.add("disabled");
  document.getElementById('gemini-text-response').innerHTML = 'asking gemini ... please wait ... <a class="btn-floating btn-large pulse"><i class="material-icons">cloud</i></a>'
  document.getElementById('gemini-image-response').innerHTML = ''
  document.getElementById('request-params').innerHTML = ''
  document.getElementById('response-metadata').innerHTML = ''

  // try {
    const response = await fetch("/gemini", {
      method: "POST",
      body: request_body,
      headers: {
        "Content-type": "application/json; charset=UTF-8"
      }
    });

    if (!response.ok) {
      console.log('error, response not ok')
      console.log(response.status)
      document.getElementById('request-params').innerHTML = "<hr><b>request params</b> <code>"+request_body+"</code>"
      document.getElementById('response-metadata').innerHTML = "<b>response metadata</b> <code>"+JSON.stringify(response)+"</code>"
    } else {
      document.getElementById('gemini-text-response').innerHTML = ''

      const data = await response.json();
      console.log('Success:', data);

      document.getElementById('request-params').innerHTML = "<hr><b>request params</b> <code>"+request_body+"</code>"
      document.getElementById('response-metadata').innerHTML = "<b>response metadata</b> <code>"+JSON.stringify(data['metadata'])+"</code>"

      if (data['html_text'] != null) {
        console.log('text is object')
        document.getElementById('gemini-text-response').innerHTML = data['html_text']
      } else {
        console.log('text is not object')
      }

      if (data['html_image'] != null) {
        console.log('image is object')
        document.getElementById('gemini-image-response').innerHTML = data['html_image']
      } else {
        console.log('img is not object')
      }
    }

    document.getElementById('ask-gemini-button').classList.remove("disabled");
    document.getElementById('prompt').classList.remove("disabled");
  

  // } catch (error) {
  //   console.error('Error:', error);
  // }

}                           

function goto_location(lat, lng, heading, pitch, zoom) {

  const newLatLng = new google.maps.LatLng(lat, lng);
  var panorama = document.map.getStreetView(); 
  panorama.setPosition(newLatLng);
  panorama.setPov({heading: heading, pitch: pitch})
  panorama.setZoom(zoom)
  document.map.setCenter(newLatLng)

  document.getElementById('gemini-text-response').innerHTML = ''  
  document.getElementById('gemini-image-response').innerHTML = ''  
  document.getElementById('request-params').innerHTML = ''  
  document.getElementById('response-metadata').innerHTML = ''  
}


function goto_usecase(prompt, lat, lng, heading, pitch, zoom) {

  document.getElementById('prompt').value = prompt
  goto_location(lat, lng, heading, pitch, zoom)

}


window.initialize = initialize;
window.call_gemini = call_gemini;
window.goto_location = goto_location;
window.goto_usecase = goto_usecase;
