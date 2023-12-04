frappe.ui.form.on('Job Card', {

    refresh: function (frm) {
        //  console.log($("[data-doctype='Leftover']"));
        if (frm.doc._causes_leftover == 0) {
            $("[data-doctype='Leftover']").hide();
            /*
              let l = cur_frm.dashboard.links_area.wrapper.find(".badge-link");
              for (const div of l) {
                  if (div.textContent.includes("Leftover")) {
                      console.log(l, div);
                      div.remove();
  
                      break;
                  }
              }
              */
            //  cur_frm.dashboard.links_area.wrapper.find(".badge-link")[3].remove();
        }
        else {
            $("[data-doctype='Leftover']").show();
        }




    },




});