// 210608 Yewon LIM ga06033@yonsei.ac.kr
// https://apis.map.kakao.com/web/sample/addr2coord/ 참고

var bttn = document.getElementById('query');
bttn.addEventListener('click', search_address);

function search_address(){
    var address = document.getElementById('data1').value;
    var time_ = parseFloat(document.getElementById('data2').value);
    
    if (time_ <= 0 || time_ > 24 || typeof(time_) != "number"){
        document.getElementById('data1').placeholder = "0 ~ 24사이 숫자로 입력해주세요";
    }
    else{
        // 주소-좌표 변환 객체를 생성합니다
	    let geocoder = new kakao.maps.services.Geocoder();
        
	    // 주소로 좌표를 검색합니다
	    geocoder.addressSearch(address, function(result, status) {
        // 정상적으로 검색이 완료됐으면 
         if (status === kakao.maps.services.Status.OK) {
            var coords = String(result[0].x) +","+ String(result[0].y);
            
            $.post( "/", {
                coordi: coords,
                time: time_
                },
                function(data){
                    var p_score = document.getElementById('score');
                    var p_comment = document.getElementById('comment');
                
                    document.getElementById('guide').className = "guide";
                    p_score.innerHTML = data + " 점";
                    p_score.className = "guide"
                    // document.getElementById('score').style.visibility = "visible";
                    var n_score = parseInt(data);
                    if (n_score >= 70){
                        p_comment.innerHTML = "  대한민국에서 제일 위험!";
                        p_comment.className = "red";
                        
                    }
                    else if(n_score >= 50 && n_score < 70){
                        p_comment.innerHTML = "  매우 위험!";
                        p_comment.className = "orange";
                        
                    }
                    else if(n_score >= 10 && n_score < 50){
                        p_comment.innerHTML = "  주의 요망!";
                        p_comment.className = "yellow";
                        
                    }
                    else{
                        p_comment.innerHTML = "  비교적 안전 :)";
                        p_comment.className = "green";
                        
                    }
                    // document.getElementById('comment').style.visibility = "visible";
                    
                    
                },
            ); 
             
		 
        } 
        else{
    	    document.getElementById('data1').placeholder = "정확한 주소를 입력해주세요 :(";
        }     
                               
        });
    }
}
