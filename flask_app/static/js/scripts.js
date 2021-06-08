// 210608 Yewon LIM ga06033@yonsei.ac.kr
// https://apis.map.kakao.com/web/sample/addr2coord/ 참고

function search_address(){
    address = document.getElementById('data1').value;
    time = document.getElementById('data2').value;
    if (time == ""){
        document.getElementById('data2').value = "시간을 입력해주세요 :("
        
    }
    else{
        // 주소-좌표 변환 객체를 생성합니다
	    let geocoder = new kakao.maps.services.Geocoder();

	    // 주소로 좌표를 검색합니다
	    geocoder.addressSearch(address, function(result, status) {
        // 정상적으로 검색이 완료됐으면 
         if (status === kakao.maps.services.Status.OK) {

            const coords = new kakao.maps.LatLng(result[0].x, result[0].y);
		    // document.getElementById('out').value = coords
            const request = new XMLHttpRequest();
            request.open('POST', '/');
            request.send()
        } 
        else{
    	    document.getElementById('data1').value = "정확한 주소를 입력해주세요 :("
        }     
                               
        });
    }
}
