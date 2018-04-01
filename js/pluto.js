var Detect = {
    init: function () {
        this.OS = this.searchString(this.dataOS);
    },
    searchString: function (data) {
        for (var i=0;i<data.length;i++) {
            var dataString = data[i].string;
            var dataProp = data[i].prop;
            if (dataString) {
                if (dataString.indexOf(data[i].subString) != -1)
                    return data[i].identity;
            }
            else if (dataProp)
                return data[i].identity;
        }
    },
    dataOS : [
        {
            string: navigator.platform,
            subString: 'Win',
            identity: 'Windows'
        },
        {
            string: navigator.platform,
            subString: 'Mac',
            identity: 'macOS'
        },
        {
            string: navigator.userAgent,
            subString: 'iPhone',
            identity: 'iOS'
        },
        {
            string: navigator.userAgent,
            subString: 'iPad',
            identity: 'iOS'
        },
        {
            string: navigator.userAgent,
            subString: 'iPod',
            identity: 'iOS'
        },
        {
            string: navigator.userAgent,
            subString: 'Android',
            identity: 'Android'
        },
        {
            string: navigator.platform,
            subString: 'Linux',
            identity: 'Linux'
        }
    ]
};

Detect.init();
if(Detect.OS=="Windows") {
    $('#download-win').addClass('featured');
} else if(Detect.OS=="macOS"){
    $('#download-mac').addClass('featured');    
} else {
    $('#download-source').addClass('featured');
}